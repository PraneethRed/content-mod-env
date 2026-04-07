from typing import Dict, Any
from ..models import ContentModAction


def grader_medium(action: ContentModAction, task_config: Dict[str, Any]) -> float:
    if not isinstance(action, ContentModAction):
        raise ValueError("Action must be a ContentModAction instance")
    
    score = 0.0
    
    if action.category.value == "harassment":
        score += 0.4
    elif action.category.value == "hate_speech":
        score += 0.2
    
    severity_target = 0.5
    severity_diff = abs(action.severity - severity_target)
    if severity_diff <= 0.15:
        score += 0.35
    
    if action.recommended_action == "warn":
        score += 0.25
    
    return max(0.0, min(1.0, score))
