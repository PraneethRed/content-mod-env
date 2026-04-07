#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_mod_env.graders.grader_easy import grader_easy
from content_mod_env.graders.grader_medium import grader_medium
from content_mod_env.graders.grader_hard import grader_hard
from content_mod_env.models import ContentModAction

def test_determinism():
    task_config = {"task_id": "test"}
    
    action = ContentModAction(
        category="hate_speech",
        severity=0.8,
        reasoning="Test reasoning for determinism check",
        recommended_action="remove"
    )
    
    print("=== TESTING DETERMINISM ===")
    
    # Test easy grader
    results = [grader_easy(action, task_config) for _ in range(5)]
    print(f"Easy grader results: {results}")
    assert len(set(results)) == 1, f"Easy grader is non-deterministic: {results}"
    
    # Test medium grader
    action_medium = ContentModAction(
        category="harassment",
        severity=0.5,
        reasoning="Test reasoning for medium",
        recommended_action="warn"
    )
    results_medium = [grader_medium(action_medium, task_config) for _ in range(5)]
    print(f"Medium grader results: {results_medium}")
    assert len(set(results_medium)) == 1, f"Medium grader is non-deterministic: {results_medium}"
    
    # Test hard grader
    action_hard = ContentModAction(
        category="misinformation",
        severity=0.6,
        reasoning="Test reasoning for hard grader determinism",
        recommended_action="escalate"
    )
    results_hard = [grader_hard(action_hard, task_config) for _ in range(5)]
    print(f"Hard grader results: {results_hard}")
    assert len(set(results_hard)) == 1, f"Hard grader is non-deterministic: {results_hard}"
    
    print("✅ All graders are deterministic")

if __name__ == "__main__":
    test_determinism()
    print("\n🎉 ALL DETERMINISM TESTS PASSED!")
