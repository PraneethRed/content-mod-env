from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class ViolationCategory(str, Enum):
    HATE_SPEECH = "hate_speech"
    HARASSMENT = "harassment"
    MISINFORMATION = "misinformation"
    SPAM = "spam"
    SAFE = "safe"


class ContentModAction(BaseModel):
    category: ViolationCategory
    severity: float = Field(ge=0.0, le=1.0)
    reasoning: str = Field(max_length=500)
    recommended_action: Literal["remove", "warn", "no_action", "escalate"]


class ContentModObservation(BaseModel):
    post_id: str
    post_text: str = Field(max_length=2000)
    author_history_score: float = Field(ge=0.0, le=1.0)
    platform_context: str
    task_id: str
    step_number: int
    goal: str


class ContentModReward(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    category_correct: bool
    severity_delta: float
    action_correct: bool
    feedback: str
