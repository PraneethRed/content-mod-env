import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from fastapi import Body

from src.content_mod_env.env import ContentModEnv
from src.content_mod_env.models import ContentModAction, ViolationCategory

app = FastAPI(title="Content Moderation Environment", version="0.1.0")

env_instances: Dict[str, ContentModEnv] = {}


def get_env(task_id: str = "easy_explicit_hate") -> ContentModEnv:
    if task_id not in env_instances:
        env_instances[task_id] = ContentModEnv(task_id)
    return env_instances[task_id]


async def safe_parse_action(raw_body: dict) -> ContentModAction:
    try:
        action_data = raw_body.get("action", raw_body)
        if isinstance(action_data, str):
            import json
            action_data = json.loads(action_data)
        if not isinstance(action_data, dict):
            action_data = {}
        if "severity" in action_data:
            action_data["severity"] = max(0.0, min(1.0, float(action_data["severity"])))
        action_data.setdefault("category", "safe")
        action_data.setdefault("severity", 0.5)
        action_data.setdefault("reasoning", "No reasoning provided")
        action_data.setdefault("recommended_action", "no_action")
        action_data["reasoning"] = str(action_data["reasoning"])[:500]
        return ContentModAction(**action_data)
    except Exception:
        return ContentModAction(
            category="safe",
            severity=0.5,
            reasoning="Fallback due to parse error",
            recommended_action="no_action"
        )


@app.post("/reset")
async def reset(request: Request):
    try:
        try:
            body = await request.json()
        except Exception:
            body = {}
        task_id = body.get("task_id") or "easy_explicit_hate"
        env = get_env(task_id)
        observation = env.reset(task_id)
        state = env.state()
        return JSONResponse({
            "observation": observation.model_dump(),
            "state": state
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=200)


@app.post("/step")
async def step(request: Request):
    try:
        try:
            body = await request.json()
        except Exception:
            body = {}
        task_id = body.get("task_id") or "easy_explicit_hate"
        env = get_env(task_id)
        action = await safe_parse_action(body)
        observation, reward, done, info = env.step(action)
        return JSONResponse({
            "observation": observation.model_dump(),
            "reward": reward.model_dump(),
            "done": done,
            "info": info
        })
    except Exception as e:
        return JSONResponse(
            {"error": str(e), "reward": {"score": 0.0}, "done": True, "info": {}},
            status_code=200
        )


@app.get("/state")
async def get_state(task_id: str = "easy_explicit_hate"):
    try:
        env = get_env(task_id)
        return JSONResponse(env.state())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=200)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": "content-moderation-env"}


@app.get("/")
async def root():
    return {
        "message": "Content Moderation Environment API",
        "version": "0.1.0",
        "endpoints": {"reset": "/reset", "step": "/step", "state": "/state", "health": "/health"},
        "tasks": ["easy_explicit_hate", "medium_passive_harassment", "hard_satire_misinformation"]
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
