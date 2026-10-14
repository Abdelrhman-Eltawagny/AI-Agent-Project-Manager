"""Project Q&A chat: the model knows the generated plan and refuses anything else.

Usage:
    python chat.py                         # uses outputs/final_project_plan.json
    python chat.py --plan outputs_7b/final_project_plan.json --model qwen2.5:7b

Guard layers (cheapest first):
  1. Deterministic: plan IDs (TASK-007, SPRINT-2...) or project keywords -> in scope.
  2. Otherwise a tiny YES/NO classifier call (max 3 tokens) decides. Unsure -> refuse.
  3. The answering prompt itself must reply OUT_OF_SCOPE for unrelated questions.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from config.settings import load_settings  # noqa: E402

OUT = "OUT_OF_SCOPE"
REFUSE_EN = "Sorry, I can only answer questions about this project's plan (tasks, sprints, team, risks, milestones)."
REFUSE_AR = "آسف، أقدر أجاوب بس على أسئلة عن خطة المشروع ده (المهام، السبرنتات، الفريق، المخاطر، المراحل)."

CJK_RE = re.compile(r"[\u3000-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uac00-\ud7af\uff00-\uffef]")
ID_RE = re.compile(r"\b(task|epic|sprint|req|risk|team|ms)[-_ ]?\d+\b", re.I)
KEYWORDS = {
    "task", "tasks", "sprint", "sprints", "epic", "epics", "project", "plan", "milestone", "milestones",
    "risk", "risks", "dependency", "dependencies", "assigned", "assignee", "assignment", "workload",
    "capacity", "estimate", "requirement", "requirements", "backlog", "deadline", "team", "priority",
    "تاسك", "تاسكات", "مهمة", "مهام", "سبرنت", "سبرنتات", "مشروع", "المشروع", "خطة", "الخطة", "فريق",
    "الفريق", "مخاطر", "ريسك", "اعتماد", "اعتماديات", "ايبك", "ابيك", "ميلستون", "متطلبات", "اولوية",
}


def is_arabic(text: str) -> bool:
    return bool(re.search(r"[\u0600-\u06FF]", text))


def refusal(question: str) -> str:
    return REFUSE_AR if is_arabic(question) else REFUSE_EN


def compact_context(plan: dict) -> str:
    """One line per item: keeps the prompt small (token-friendly)."""
    p = plan.get("project", {})
    team = {m["id"]: m for m in plan.get("team", [])}
    sprint_of = {t: s["number"] for s in plan.get("sprints", []) for t in s.get("task_ids", [])}
    owner = {a["task_id"]: a["member_id"] for a in plan.get("assignments", [])}
    deps: dict[str, list[str]] = {}
    for d in plan.get("dependencies", []):
        deps.setdefault(d["task_id"], []).append(d["depends_on"])

    lines = [f"PROJECT: {p.get('name')} | {p.get('duration_weeks')} weeks, {p.get('sprint_count')} sprints",
             f"OBJECTIVE: {p.get('objective')}",
             "OUT OF SCOPE: " + "; ".join(p.get("out_of_scope", [])), "EPICS:"]
    lines += [f"{e['id']} {e['name']} [{e['priority']}]" for e in plan.get("epics", [])]
    lines.append("TASKS (id | title | type | hours | priority | epic | sprint | owner | depends_on):")
    for t in plan.get("tasks", []):
        o = team.get(owner.get(t["id"], ""), {}).get("name", "unassigned")
        lines.append(f"{t['id']} | {t['title']} | {t['type']} | {t['estimated_hours']}h | {t['priority']} | "
                     f"{t['epic_id']} | S{sprint_of.get(t['id'], '?')} | {o} | {','.join(deps.get(t['id'], [])) or '-'}")
    lines.append("SPRINTS:")
    lines += [f"S{s['number']} goal: {s['goal']} | planned {s['planned_hours']}h of {s['capacity_hours']}h"
              for s in plan.get("sprints", [])]
    lines.append("TEAM:")
    lines += [f"{m['id']} {m['name']} ({m['role']}) skills: {', '.join(m['skills'])} | {m['capacity_hours_per_sprint']}h/sprint"
              for m in plan.get("team", [])]
    lines.append("RISKS:")
    lines += [f"{r['id']} {r['title']} (likelihood {r['likelihood']}, impact {r['impact']}): {r['mitigation']}"
              for r in plan.get("risks", [])]
    lines.append("MILESTONES:")
    lines += [f"{m['id']} week {m['week']}: {m['name']}" for m in plan.get("milestones", [])]
    return "\n".join(lines)


def deterministic_in_scope(question: str) -> bool:
    if ID_RE.search(question):
        return True
    words = set(re.findall(r"\w+", question.lower()))
    return bool(words & KEYWORDS)


class Chat:
    def __init__(self, plan: dict, model: str, base_url: str, timeout: float = 300, keep_alive: str = "30m"):
        self.plan, self.model, self.base_url = plan, model, base_url.rstrip("/")
        self.timeout, self.keep_alive = timeout, keep_alive
        self.context = compact_context(plan)
        p = plan.get("project", {})
        self.topic = f"{p.get('name')}: {p.get('summary')}"
        self.history: list[dict] = []

    # --- LLM plumbing (overridable in tests) ---
    def _chat(self, messages: list[dict], max_tokens: int, temperature: float = 0.1) -> str:
        resp = httpx.post(f"{self.base_url}/api/chat", timeout=self.timeout, json={
            "model": self.model, "stream": False, "keep_alive": self.keep_alive, "messages": messages,
            "options": {"temperature": temperature, "num_predict": max_tokens, "num_ctx": 8192}})
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()

    def classify(self, question: str) -> bool:
        prompt = (f"Project: {self.topic}\nQuestion: {question}\n"
                  "Is the question about this project, its plan, tasks, sprints, team members, schedule, "
                  "risks or requirements? Answer with exactly one word: YES or NO.")
        return self._chat([{"role": "user", "content": prompt}], max_tokens=3, temperature=0).upper().startswith("YES")

    def in_scope(self, question: str) -> bool:
        return deterministic_in_scope(question) or self.classify(question)

    def ask(self, question: str) -> str:
        if not self.in_scope(question):
            return refusal(question)
        system = (
            "You are the assistant for ONE project, described below. Answer ONLY from this project data. "
            f"If the question is not about this project, reply with exactly {OUT} and nothing else. "
            "If it is about the project but the data does not contain the answer, say so briefly. "
            "Be concise. Reply ONLY in the user's language (Arabic or English). NEVER use Chinese or any other "
            "language. Keep task IDs and names as written.\n\n"
            + self.context)
        msgs = [{"role": "system", "content": system}, *self.history[-6:], {"role": "user", "content": question}]
        answer = self._chat(msgs, max_tokens=400)
        if CJK_RE.search(answer):  # Qwen sometimes code-switches to Chinese: retry once, then strip
            msgs[-1] = {"role": "user", "content": question + "\n(Answer in Arabic or English only. No Chinese.)"}
            answer = self._chat(msgs, max_tokens=400)
            answer = re.sub(r"\s{2,}", " ", CJK_RE.sub("", answer)).strip()
        if answer.strip().upper().startswith(OUT):
            return refusal(question)
        self.history += [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]
        return answer


def main(argv=None) -> int:
    s = load_settings()
    ap = argparse.ArgumentParser(description="Ask questions about the generated project plan.")
    ap.add_argument("--plan", default=str(ROOT / s.output_dir / "final_project_plan.json"))
    ap.add_argument("--model", default=s.model)
    args = ap.parse_args(argv)
    path = Path(args.plan)
    if not path.exists():
        print(f"Plan not found: {path}. Run main.py first.")
        return 1
    chat = Chat(json.loads(path.read_text(encoding="utf-8")), args.model, s.ollama_base_url,
                s.llm_timeout_seconds, s.keep_alive)
    print(f"Model: {args.model} | Plan: {path.name} | type 'exit' to quit")
    while True:
        try:
            q = input("\nYou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"exit", "quit", "خروج"}:
            break
        if not q:
            continue
        try:
            print("\nBot>", chat.ask(q))
        except httpx.HTTPError as exc:
            print(f"\n[ERROR] Cannot reach Ollama / model: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
