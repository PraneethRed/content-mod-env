from typing import Dict, Any
from ..models import ContentModAction


def grader_hard(action: ContentModAction, task_config: Dict[str, Any]) -> float:
    if not isinstance(action, ContentModAction):
        raise ValueError("Action must be a ContentModAction instance")
    
    score = 0.0
    
    if action.category.value == "misinformation":
        score += 0.4
    elif action.category.value == "spam":
        score += 0.1
    elif action.category.value == "safe":
        score += 0.1
    
    severity_target = 0.6
    severity_diff = abs(action.severity - severity_target)
    if severity_diff <= 0.2:
        score += 0.3
    
    if action.recommended_action == "escalate":
        score += 0.2
    elif action.recommended_action == "remove":
        score -= 0.1
    
    if len(action.reasoning.strip()) < 20:
        score -= 0.2
    
    if "satire" in action.reasoning.lower() and "misinformation" in action.category.value:
        score += 0.1
    
    return max(0.0, min(1.0, score))
