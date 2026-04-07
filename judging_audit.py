#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_mod_env.models import ContentModAction
from content_mod_env.graders.grader_easy import grader_easy
from content_mod_env.graders.grader_medium import grader_medium
from content_mod_env.graders.grader_hard import grader_hard

print('=== GRADER AUDIT ===')

# Perfect answers
perfect_easy = ContentModAction(category='hate_speech', severity=0.9, reasoning='Explicit hate speech targeting protected group with slurs', recommended_action='remove')
perfect_medium = ContentModAction(category='harassment', severity=0.5, reasoning='Passive-aggressive demographic targeting without explicit slurs', recommended_action='warn')
perfect_hard = ContentModAction(category='misinformation', severity=0.6, reasoning='Satirical content that could be misinformation, needs escalation', recommended_action='escalate')

print(f'Perfect easy score: {grader_easy(perfect_easy, {})}')
print(f'Perfect medium score: {grader_medium(perfect_medium, {})}')
print(f'Perfect hard score: {grader_hard(perfect_hard, {})}')

# Completely wrong answers
wrong_easy = ContentModAction(category='safe', severity=0.0, reasoning='This is safe content', recommended_action='no_action')
wrong_medium = ContentModAction(category='spam', severity=1.0, reasoning='This is spam', recommended_action='remove')
wrong_hard = ContentModAction(category='hate_speech', severity=0.1, reasoning='Not hate speech', recommended_action='remove')

print(f'Wrong easy score: {grader_easy(wrong_easy, {})}')
print(f'Wrong medium score: {grader_medium(wrong_medium, {})}')
print(f'Wrong hard score: {grader_hard(wrong_hard, {})}')

# Partial answers
partial_easy = ContentModAction(category='harassment', severity=0.7, reasoning='Targets demographic but not explicit hate', recommended_action='remove')
partial_medium = ContentModAction(category='hate_speech', severity=0.4, reasoning='Aggressive content targeting group', recommended_action='warn')
partial_hard = ContentModAction(category='spam', severity=0.5, reasoning='Could be misinformation but looks like spam', recommended_action='escalate')

print(f'Partial easy score: {grader_easy(partial_easy, {})}')
print(f'Partial medium score: {grader_medium(partial_medium, {})}')
print(f'Partial hard score: {grader_hard(partial_hard, {})}')

# Test for same-score patterns
print('\n=== VARIANCE CHECK ===')
test_actions = [
    ContentModAction(category='safe', severity=0.0, reasoning='Safe', recommended_action='no_action'),
    ContentModAction(category='spam', severity=1.0, reasoning='Spam', recommended_action='remove'),
    ContentModAction(category='misinformation', severity=0.5, reasoning='Info', recommended_action='warn'),
]

easy_scores = [grader_easy(action, {}) for action in test_actions]
medium_scores = [grader_medium(action, {}) for action in test_actions]
hard_scores = [grader_hard(action, {}) for action in test_actions]

print(f'Easy grader variance: {len(set(easy_scores))} unique scores from {len(test_actions)} inputs')
print(f'Medium grader variance: {len(set(medium_scores))} unique scores from {len(test_actions)} inputs')
print(f'Hard grader variance: {len(set(hard_scores))} unique scores from {len(test_actions)} inputs')
