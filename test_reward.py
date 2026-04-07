#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_mod_env.env import compute_reward
from content_mod_env.models import ContentModAction

def test_reward_function():
    print("=== TESTING REWARD FUNCTION ===")
    
    # Test 1: Perfect answer
    action_perfect = ContentModAction(
        category="hate_speech",
        severity=0.8,
        reasoning="Post contains explicit hate speech targeting protected group",
        recommended_action="remove"
    )
    ground_truth_perfect = {
        "category": "hate_speech",
        "severity_target": 0.8,
        "recommended_action": "remove",
        "related_categories": ["harassment"]
    }
    reward_perfect = compute_reward(action_perfect, ground_truth_perfect)
    print(f"Perfect answer reward: {reward_perfect.score}")
    assert 0.8 <= reward_perfect.score <= 1.0, f"Perfect answer should score high, got {reward_perfect.score}"
    
    # Test 2: Contradiction detection (low severity + remove action)
    action_contradiction = ContentModAction(
        category="hate_speech",
        severity=0.1,
        reasoning="Some reasoning",
        recommended_action="remove"
    )
    reward_contradiction = compute_reward(action_contradiction, ground_truth_perfect)
    print(f"Contradiction reward: {reward_contradiction.score}")
    assert reward_contradiction.score < reward_perfect.score, "Contradiction should be penalized"
    
    # Test 3: Related category partial credit
    action_related = ContentModAction(
        category="harassment",
        severity=0.8,
        reasoning="Harassment content",
        recommended_action="remove"
    )
    reward_related = compute_reward(action_related, ground_truth_perfect)
    print(f"Related category reward: {reward_related.score}")
    assert 0.0 < reward_related.score < reward_perfect.score, "Related category should get partial credit"
    
    # Test 4: All scores in [0.0, 1.0]
    test_actions = [
        ContentModAction(category="safe", severity=0.0, reasoning="Safe content", recommended_action="no_action"),
        ContentModAction(category="spam", severity=1.0, reasoning="Spam content", recommended_action="remove"),
        ContentModAction(category="misinformation", severity=0.5, reasoning="Misinfo", recommended_action="warn"),
    ]
    
    for i, action in enumerate(test_actions):
        reward = compute_reward(action, ground_truth_perfect)
        assert 0.0 <= reward.score <= 1.0, f"Score {reward.score} out of bounds for action {i}"
        print(f"Action {i} score: {reward.score}")
    
    # Test 5: Non-binary reward signals (at least 5 unique scores from 10 actions)
    scores = set()
    for i in range(10):
        action = ContentModAction(
            category=["hate_speech", "harassment", "safe", "spam", "misinformation"][i % 5],
            severity=0.1 + (i * 0.1),
            reasoning=f"Test reasoning {i}",
            recommended_action=["remove", "warn", "no_action", "escalate"][i % 4]
        )
        reward = compute_reward(action, ground_truth_perfect)
        scores.add(round(reward.score, 3))
    
    print(f"Unique scores from 10 actions: {len(scores)} scores: {sorted(scores)}")
    assert len(scores) >= 5, f"Need at least 5 unique scores, got {len(scores)}: {scores}"
    
    print("✅ All reward function tests passed")

if __name__ == "__main__":
    test_reward_function()
    print("\n🎉 ALL REWARD FUNCTION TESTS PASSED!")
