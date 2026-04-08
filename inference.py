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
async def step(request: StepRequest = Body(default=StepRequest()))
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
    
    # Check if we have API credentials
    if not API_KEY:
        print("Warning: No API credentials found. Running in server mode only.")
        print("Set HF_TOKEN or API_KEY environment variable to run full inference.")
    else:
        # Initialize OpenAI client
        client = OpenAI(
            api_key=API_KEY,
            base_url=API_BASE_URL
        )
        
        tasks = ["easy_explicit_hate", "medium_passive_harassment", "hard_satire_misinformation"]
        scores = {}
        
        for i, task_id in enumerate(tasks, 1):
            print(f"[STEP {i}] Running task: {task_id}")
            
            # Initialize environment
            env = ContentModEnv(task_id)
            observation = env.reset()
            
            # Create prompt for LLM
            prompt = f"""
You are a content moderator. Review this post and decide on appropriate action.

Post: "{observation.post_text}"
Author History Score: {observation.author_history_score}
Platform Context: {observation.platform_context}
Goal: {observation.goal}

Respond with JSON:
{{
    "category": "hate_speech|harassment|misinformation|spam|safe",
    "severity": 0.0-1.0,
    "reasoning": "Brief explanation",
    "recommended_action": "remove|warn|no_action|escalate"
}}
"""
            
            try:
                # Get LLM response
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.1
                )
                
                response_text = response.choices[0].message.content.strip()
                action_data = json.loads(response_text)
                action = ContentModAction(**action_data)
                
                # Take step in environment
                obs, reward, done, info = env.step(action)
                
                # Get grader score
                grader = get_grader(task_id)
                grader_score = grader(action, {"task_id": task_id})
                
                scores[task_id] = {
                    "reward_score": reward.score,
                    "grader_score": grader_score
                }
                
                print(f"Task {task_id} - Reward: {reward.score:.3f}, Grader: {grader_score:.3f}")
                
            except Exception as e:
                print(f"Error in task {task_id}: {e}")
                scores[task_id] = {"reward_score": 0.0, "grader_score": 0.0}
        
        print("[END] Inference complete")
        print("Final scores:")
        for task_id, score_dict in scores.items():
            print(f"  {task_id}: Reward={score_dict['reward_score']:.3f}, Grader={score_dict['grader_score']:.3f}")
    
    # Start FastAPI server
    print("Starting FastAPI server...")
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)
