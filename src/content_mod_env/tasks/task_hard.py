import uuid
from typing import Dict, Tuple, Any
from ..models import ContentModAction


class HardTask:
    def __init__(self):
        self.posts = [
            {
                "post_text": "BREAKING: Senator Johnson caught in secret deal with foreign corporation! Sources say he sold votes for campaign donations. This corruption must stop! #Politics #Corruption",
                "author_history_score": 0.2,
                "platform_context": "news_platform",
                "goal": "Determine if this is misinformation or protected political speech"
            },
            {
                "post_text": "Scientists confirm that drinking bleach cures COVID-19! Big Pharma is hiding the cure to sell expensive vaccines. Share this truth before it gets deleted! #Health #Truth",
                "author_history_score": 0.7,
                "platform_context": "health_forum",
                "goal": "Determine if this is dangerous misinformation or protected speech"
            },
            {
                "post_text": "SATIRE: Local man discovers that government is actually run by lizard people in human suits. 'I always knew something was off,' he says while adjusting his tin foil hat.",
                "author_history_score": 0.1,
                "platform_context": "satire_platform",
                "goal": "Identify satirical content vs actual misinformation"
            }
        ]
    
    def generate_post(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        import random
        post_data = random.choice(self.posts).copy()
        post_data["post_id"] = str(uuid.uuid4())
        
        ground_truth = {
            "category": "misinformation",
            "severity_target": 0.6,
            "recommended_action": "escalate",
            "related_categories": ["spam", "safe"]
        }
        
        return post_data, ground_truth
    
    def should_end_episode(self, step_count: int, action: ContentModAction) -> bool:
        return step_count >= 3
