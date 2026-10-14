# Deployment

## Docker Compose (Ollama + web app)

`docker-compose.prod.yml` runs two services on one server:

- `ollama`: Ollama with a persistent model volume (optional Nvidia GPU block, commented in the file)
- `web`: FastAPI/uvicorn on port 8000, reading the plan read-only from `./plan/final_project_plan.json`

```bash
cp .env.example .env                         # set API_KEY (required) and optionally PM_MODEL
cp examples/outputs/clinic_7b/final_project_plan.json plan/final_project_plan.json
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec ollama ollama pull qwen2.5:7b     # first time only
```

Open `http://SERVER_IP:8000`.

The compose file refuses to start without `API_KEY` (`${API_KEY:?Set API_KEY in .env}`) and defaults `PM_MODEL` to `qwen2.5:7b`.

## GPU

Uncomment the `deploy.resources.reservations.devices` block under the `ollama` service and install the NVIDIA Container Toolkit on the host. A GPU should shorten planning runs (the recorded 7B runs took 18-59 minutes; the hardware used was not recorded).

## Image

The `Dockerfile` uses `python:3.11-slim` plus build tools (some CrewAI dependencies compile native extensions). Its default command runs the self-test on the bundled sample document (`python main.py --test`), which needs a reachable Ollama server; add `--mock` for an offline check.

## Production notes

- Put the service behind HTTPS (reverse proxy) when it is reachable from a network.
- The API key is a single shared secret; there are no per-user accounts yet.
- Sessions are kept in memory (up to 200 conversations, oldest evicted).
- The assistant reads one plan file; regenerate it with `main.py` and replace `plan/final_project_plan.json`.
