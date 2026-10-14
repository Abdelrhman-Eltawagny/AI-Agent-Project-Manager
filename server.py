"""Web server: browser chat + REST API over the scoped project assistant.

Run:  uvicorn server:app --host 0.0.0.0 --port 8000
Env:  PLAN_PATH (plan json), API_KEY (optional but recommended), PM_MODEL, PM_OLLAMA_URL
"""
from __future__ import annotations

import json
import os
import secrets
from collections import OrderedDict
from pathlib import Path

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from chat import Chat
from config.settings import load_settings

ROOT = Path(__file__).resolve().parent
S = load_settings()
PLAN_PATH = Path(os.environ.get("PLAN_PATH") or ROOT / S.output_dir / "final_project_plan.json")
API_KEY = os.environ.get("API_KEY", "")
MAX_SESSIONS = 200

app = FastAPI(title="Project Assistant")
_plan: dict | None = None
_sessions: OrderedDict[str, Chat] = OrderedDict()


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    session_id: str = Field("default", max_length=64)


def _chat_for(sid: str) -> Chat:
    global _plan
    if _plan is None:
        if not PLAN_PATH.exists():
            raise HTTPException(503, f"Plan file not found: {PLAN_PATH}")
        _plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    if sid not in _sessions:
        _sessions[sid] = Chat(_plan, S.model, S.ollama_base_url, S.llm_timeout_seconds, S.keep_alive)
        while len(_sessions) > MAX_SESSIONS:
            _sessions.popitem(last=False)
    _sessions.move_to_end(sid)
    return _sessions[sid]


@app.get("/health")
def health():
    return {"status": "ok", "model": S.model, "plan_loaded": PLAN_PATH.exists()}


@app.post("/ask")
def ask(q: Question, x_api_key: str | None = Header(default=None)):
    if API_KEY and not secrets.compare_digest(x_api_key or "", API_KEY):
        raise HTTPException(401, "Invalid or missing API key")
    chat = _chat_for(q.session_id)
    try:
        return {"answer": chat.ask(q.question)}
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Model unavailable: {exc}")


PAGE = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Project Assistant</title><style>
body{font-family:system-ui,sans-serif;max-width:720px;margin:0 auto;padding:16px;background:#f5f5f7}
#log{height:65vh;overflow:auto;background:#fff;border-radius:10px;padding:12px;border:1px solid #ddd}
.m{margin:8px 0;padding:8px 12px;border-radius:10px;white-space:pre-wrap;max-width:85%}
.u{background:#dbeafe;margin-left:auto}.b{background:#eee}form{display:flex;gap:8px;margin-top:10px}
input{flex:1;padding:10px;border-radius:8px;border:1px solid #bbb}button{padding:10px 16px;border:0;border-radius:8px;background:#2563eb;color:#fff}
</style><h2>Project Assistant</h2><div id="log"></div>
<form id="f"><input id="q" dir="auto" placeholder="Ask about tasks, sprints, team..." autocomplete="off" required><button>Send</button></form>
<script>
const sid=localStorage.sid||(localStorage.sid=Math.random().toString(36).slice(2)),log=document.getElementById('log');
const add=(t,c)=>{const d=document.createElement('div');d.className='m '+c;d.dir='auto';d.textContent=t;log.append(d);log.scrollTop=1e9;return d};
f.onsubmit=async e=>{e.preventDefault();const t=q.value;q.value='';add(t,'u');const w=add('...','b');
 const h={'Content-Type':'application/json'};const k=sessionStorage.getItem('k');if(k)h['x-api-key']=k;
 let r=await fetch('/ask',{method:'POST',headers:h,body:JSON.stringify({question:t,session_id:sid})});
 if(r.status==401){const n=prompt('API key:')||'';sessionStorage.setItem('k',n);h['x-api-key']=n;
  r=await fetch('/ask',{method:'POST',headers:h,body:JSON.stringify({question:t,session_id:sid})})}
 w.textContent=r.ok?(await r.json()).answer:'Error '+r.status};
</script></html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    return PAGE
