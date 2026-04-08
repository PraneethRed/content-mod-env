import os
import uuid
from typing import Dict, Any, Tuple, Optional
from .models import (
    ContentModAction,
    ContentModObservation,
    ContentModReward,
    ViolationCategory,
)
from .tasks.task_easy import EasyTask
from .tasks.task_medium import MediumTask
from .tasks.task_hard import HardTask


def compute_reward(action: ContentModAction, ground_truth: dict) -> ContentModReward:
    score = 0.0
    category_correct = action.category == ground_truth["category"]
    severity_delta = abs(action.severity - ground_truth["severity_target"])
    action_correct = action.recommended_action == ground_truth["recommended_action"]
    
    if category_correct:
        score += 0.4
    else:
        if action.category in ground_truth.get("related_categories", []):
            score += 0.15
    
    severity_score = max(0.0, 0.3 - (severity_delta * 0.3 / 0.3))
    score += severity_score
    
    if action_correct:
        score += 0.2
    
    reasoning = action.reasoning.lower()


    if len(reasoning) > 40:
        score += 0.05


    if any(word in reasoning for word in ["policy", "guideline", "harm", "context"]):
        score += 0.05
    
    if action.severity < 0.3 and action.recommended_action == "remove":
        score -= 0.15
  
    return ContentModReward(
        score=max(0.0, min(1.0, score)),
        category_correct=category_correct,
        severity_delta=severity_delta,
        action_correct=action_correct,
        feedback=f"Category: {'✓' if category_correct else '✗'}, Severity delta: {severity_delta:.2f}"
    )


class ContentModEnv:
    def __init__(self, task_id: str = "easy_explicit_hate"):
        self.task_id = task_id
        self.task = self._get_task(task_id)
        self.episode_count = 0
        self.step_count = 0
        self.episode_reward = 0.0
        self.current_observation: Optional[ContentModObservation] = None
        self.ground_truth: Optional[dict] = None
        
    def _get_task(self, task_id: str):
        tasks = {
            "easy_explicit_hate": EasyTask(),
            "medium_passive_harassment": MediumTask(),
            "hard_satire_misinformation": HardTask(),
        }
        if task_id not in tasks:
            raise ValueError(f"Unknown task_id: {task_id}")
        return tasks[task_id]
    
    def reset(self, task_id: Optional[str] = None) -> ContentModObservation:
        if task_id:
            self.task_id = task_id
            self.task = self._get_task(task_id)
        
        self.episode_count += 1
        self.step_count = 0
        self.episode_reward = 0.0
        
        post_data, ground_truth = self.task.generate_post()
        self.ground_truth = ground_truth
        
        self.current_observation = ContentModObservation(
            post_id=post_data["post_id"],
            post_text=post_data["post_text"][:2000],
            author_history_score=post_data["author_history_score"],
            platform_context=post_data["platform_context"],
            task_id=self.task_id,
            step_number=self.step_count,
            goal=post_data["goal"]
        )
        
        return self.current_observation
    
    def step(self, action: ContentModAction) -> Tuple[ContentModObservation, ContentModReward, bool, Dict[str, Any]]:
        if not isinstance(action, ContentModAction):
            raise ValueError("Action must be a ContentModAction instance")
        
        if not self.ground_truth:
            raise ValueError("Environment not reset. Call reset() first.")
        
        self.step_count += 1
        
        reward = compute_reward(action, self.ground_truth)
        self.episode_reward += reward.score
        
        done = self.task.should_end_episode(self.step_count, action)
        
        if done:
            info = {
                "episode_reward": self.episode_reward,
                "episode_length": self.step_count,
                "task_id": self.task_id,
                "ground_truth": self.ground_truth,
            }
            dummy_obs = ContentModObservation(
                post_id="",
                post_text="",
                author_history_score=0.0,
                platform_context="",
                task_id=self.task_id,
                step_number=self.step_count,
                goal="Episode complete"
            )
            return dummy_obs, reward, done, info
        else:
            next_post_data, next_ground_truth = self.task.generate_post()
            self.ground_truth = next_ground_truth
            
            next_observation = ContentModObservation(
                post_id=next_post_data["post_id"],
                post_text=next_post_data["post_text"][:2000],
                author_history_score=next_post_data["author_history_score"],
                platform_context=next_post_data["platform_context"],
                task_id=self.task_id,
                step_number=self.step_count,
                goal=next_post_data["goal"]
            )
            
            info = {
                "step_reward": reward.score,
                "episode_reward_so_far": self.episode_reward,
                "task_id": self.task_id,
            }
            
            return next_observation, reward, done, info
    
    def state(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "episode_count": self.episode_count,
            "step_count": self.step_count,
            "episode_reward": self.episode_reward,
            "current_observation": self.current_observation.model_dump() if self.current_observation else None,
            "ground_truth": self.ground_truth,
        }
