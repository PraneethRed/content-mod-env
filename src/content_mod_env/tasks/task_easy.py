import uuid
from typing import Dict, Tuple, Any
from ..models import ContentModAction


class EasyTask:
    def __init__(self):
        self.posts = [
            {
                "post_text": "I hate all people from [country] and they should be banned from our country. They are disgusting and don't deserve to live here.",
                "author_history_score": 0.8,
                "platform_context": "general_social_media",
                "goal": "Identify and remove explicit hate speech"
            },
            {
                "post_text": "All [religious_group] members are terrorists and should be eliminated. We need to get rid of them before they destroy our society.",
                "author_history_score": 0.9,
                "platform_context": "political_forum",
                "goal": "Identify and remove explicit hate speech"
            },
            {
                "post_text": "[ethnic_group] people are inferior and stupid. They shouldn't be allowed to vote or hold jobs. Send them back where they came from!",
                "author_history_score": 0.85,
                "platform_context": "general_social_media",
                "goal": "Identify and remove explicit hate speech"
            }
        ]
    
    def generate_post(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        import random
        post_data = random.choice(self.posts).copy()
        post_data["post_id"] = str(uuid.uuid4())
        
        ground_truth = {
            "category": "hate_speech",
            "severity_target": 0.8,
            "recommended_action": "remove",
            "related_categories": ["harassment"]
        }
        
        return post_data, ground_truth
    
    def should_end_episode(self, step_count: int, action: ContentModAction) -> bool:
        return step_count >= 1
