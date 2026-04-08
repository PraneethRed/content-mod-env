import os
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from openai import OpenAI

from src.content_mod_env.env import ContentModEnv
from src.content_mod_env.models import ContentModAction, ContentModObservation, ContentModReward
from src.content_mod_env.graders.grader_easy import grader_easy
from src.content_mod_env.graders.grader_medium import grader_medium
from src.content_mod_env.graders.grader_hard import grader_hard

# Environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")


class ResetRequest(BaseModel):
    task_id: Optional[str] = None


class StepRequest(BaseModel):
    action: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None


class ResetResponse(BaseModel):
    observation: Dict[str, Any]
    state: Dict[str, Any]


class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: Dict[str, Any]
    done: bool
    info: Dict[str, Any]


app = FastAPI(title="Content Moderation Environment", version="0.1.0")

env_instances: Dict[str, ContentModEnv] = {}


def get_env(task_id: str = "easy_explicit_hate") -> ContentModEnv:
    if task_id not in env_instances:
        env_instances[task_id] = ContentModEnv(task_id)
    return env_instances[task_id]


def get_grader(task_id: str):
    graders = {
        "easy_explicit_hate": grader_easy,
        "medium_passive_harassment": grader_medium,
        "hard_satire_misinformation": grader_hard,
    }
    return graders.get(task_id, grader_easy)


from fastapi import Body

@app.post("/reset", response_model=ResetResponse)
async def reset(request: ResetRequest = Body(default=ResetRequest())):
    try:
        task_id = request.task_id or "easy_explicit_hate"
        env = get_env(task_id)
        observation = env.reset(task_id if request.task_id else None)
        state = env.state()
        
        return ResetResponse(
            observation=observation.model_dump(),
            state=state
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/step", response_model=StepResponse)
async def step(request: StepRequest = Body(default=StepRequest())):
    try:
        task_id = request.task_id or "easy_explicit_hate"
        env = get_env(task_id)
        
        action_data = request.action
        action = ContentModAction(**action_data)
        
        observation, reward, done, info = env.step(action)
        
        grader = get_grader(task_id)
        grader_score = grader(action, {"task_id": task_id})
        info["grader_score"] = grader_score
        
        return StepResponse(
            observation=observation.model_dump(),
            reward=reward.model_dump(),
            done=done,
            info=info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state")
async def get_state(task_id: str = "easy_explicit_hate"):
    try:
        env = get_env(task_id)
        return env.state()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": "content-moderation-env"}


@app.get("/")
async def root():
    return {
        "message": "Content Moderation Environment API",
        "version": "0.1.0",
        "endpoints": {
            "reset": "/reset",
            "step": "/step", 
            "state": "/state",
            "health": "/health"
        },
        "tasks": [
            "easy_explicit_hate",
            "medium_passive_harassment", 
            "hard_satire_misinformation"
        ]
    }


if __name__ == "__main__":
    print("[START] Content Moderation Environment Inference")
    # Start FastAPI server
    print("Starting FastAPI server...")
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
