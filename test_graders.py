#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_mod_env.models import ContentModAction
from content_mod_env.graders.grader_easy import grader_easy
from content_mod_env.graders.grader_medium import grader_medium
from content_mod_env.graders.grader_hard import grader_hard

def test_graders():
    task_config = {"task_id": "test"}
    
    print("=== TESTING EASY GRADER ===")
    
    # Perfect answer
    action_perfect = ContentModAction(
        category="hate_speech", 
        severity=0.9,
        reasoning="Post contains explicit slurs targeting a racial group with intent to demean",
        recommended_action="remove"
    )
    score_perfect = grader_easy(action_perfect, task_config)
    print(f"Perfect answer score: {score_perfect}")
    assert score_perfect >= 0.85, f"Perfect score should be >= 0.85, got {score_perfect}"
    
    # Wrong category
    action_wrong_cat = ContentModAction(
        category="safe",  # Completely wrong category
        severity=0.1,  # Wrong severity too
        reasoning="This is safe content",
        recommended_action="warn"  # Wrong action too
    )
    score_wrong = grader_easy(action_wrong_cat, task_config)
    print(f"Wrong category score: {score_wrong}")
    assert 0.0 <= score_wrong <= 0.5, f"Wrong category should be partial or zero, got {score_wrong}"
    
    # Empty reasoning
    action_no_reason = ContentModAction(
        category="hate_speech", 
        severity=0.9,
        reasoning="bad",
        recommended_action="remove"
    )
    score_no_reason = grader_easy(action_no_reason, task_config)
    print(f"No reasoning score: {score_no_reason}")
    assert score_no_reason < score_perfect, "Empty reasoning should score lower"
    
    # Variance check
    scores = [score_perfect, score_wrong]
    assert scores[0] != scores[1], "Scores must vary"
    print("✅ Easy grader tests passed")
    
    print("\n=== TESTING MEDIUM GRADER ===")
    
    # Perfect answer
    action_medium_perfect = ContentModAction(
        category="harassment", 
        severity=0.5,
        reasoning="Passive-aggressive content targeting demographic group",
        recommended_action="warn"
    )
    score_medium_perfect = grader_medium(action_medium_perfect, task_config)
    print(f"Medium perfect score: {score_medium_perfect}")
    
    # Related category
    action_related = ContentModAction(
        category="hate_speech", 
        severity=0.5,
        reasoning="Targets demographic group",
        recommended_action="warn"
    )
    score_related = grader_medium(action_related, task_config)
    print(f"Related category score: {score_related}")
    assert score_related < score_medium_perfect, "Related category should score lower"
    
    print("✅ Medium grader tests passed")
    
    print("\n=== TESTING HARD GRADER ===")
    
    # Perfect answer
    action_hard_perfect = ContentModAction(
        category="misinformation", 
        severity=0.6,
        reasoning="Satirical content that could be misinformation, needs escalation",
        recommended_action="escalate"
    )
    score_hard_perfect = grader_hard(action_hard_perfect, task_config)
    print(f"Hard perfect score: {score_hard_perfect}")
    
    # Too aggressive
    action_aggressive = ContentModAction(
        category="misinformation", 
        severity=0.6,
        reasoning="Satirical content that could be misinformation, needs escalation",
        recommended_action="remove"
    )
    score_aggressive = grader_hard(action_aggressive, task_config)
    print(f"Too aggressive score: {score_aggressive}")
    assert score_aggressive < score_hard_perfect, "Too aggressive should score lower"
    
    print("✅ Hard grader tests passed")

if __name__ == "__main__":
    test_graders()
    print("\n🎉 ALL GRADER TESTS PASSED!")
