import uuid
from typing import Dict, Tuple, Any
from ..models import ContentModAction
import random


class MediumTask:
    def __init__(self):
        self.posts = [
            {
                "post_text": "It's interesting how some people from certain neighborhoods always seem to get into trouble. Maybe there's a cultural pattern there that we should discuss.",
                "author_history_score": 0.4,
                "platform_context": "community_forum",
                "goal": "Identify passive-aggressive demographic targeting"
            },
            {
                "post_text": "I'm not saying all immigrants are bad, but we should really think about whether people from certain countries share our values. Just something to consider.",
                "author_history_score": 0.3,
                "platform_context": "political_discussion",
                "goal": "Identify passive-aggressive demographic targeting"
            },
            {
                "post_text": "You have to wonder why some communities always struggle economically. Perhaps it's related to their work ethic or priorities in life.",
                "author_history_score": 0.5,
                "platform_context": "economic_forum",
                "goal": "Identify passive-aggressive demographic targeting"
            },
            {
                "post_text": "Wow great job genius, really impressive work there.",
                "author_history_score": 0.35,
                "platform_context": "gaming_forum",
                "goal": "Detect passive aggressive harassment disguised as sarcasm"
            }
        ]
    
    def generate_post(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        import random
        post_data = random.choice(self.posts).copy()
        post_data["post_id"] = str(uuid.uuid4())
        
        ground_truth = {
            "category": "harassment",
            "severity_target": 0.5 + random.uniform(-0.05, 0.05),
            "recommended_action": "warn",
            "related_categories": ["hate_speech"]
        }
        
        return post_data, ground_truth
    
    def should_end_episode(self, step_count: int, action: ContentModAction) -> bool:
        return step_count >= 1
