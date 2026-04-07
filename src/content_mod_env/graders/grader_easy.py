from typing import Dict, Any
from ..models import ContentModAction


def grader_easy(action: ContentModAction, task_config: Dict[str, Any]) -> float:
    if not isinstance(action, ContentModAction):
        raise ValueError("Action must be a ContentModAction instance")
    
    score = 0.0
    
    if action.category.value == "hate_speech":
        score += 0.5
    elif action.category.value in ["harassment"]:  # Related category
        score += 0.15
    
    severity_target = 0.8
    severity_diff = abs(action.severity - severity_target)
    if severity_diff <= 0.2:
        score += 0.3
    
    if action.recommended_action == "remove":
        score += 0.2
    
    # Reasoning quality penalty
    if len(action.reasoning.strip()) < 20:
        score -= 0.1
    
    return max(0.0, min(1.0, score))
