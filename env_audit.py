#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_mod_env.env import ContentModEnv
from content_mod_env.models import ContentModAction

print('=== ENVIRONMENT DESIGN AUDIT ===')

# Test state isolation
env = ContentModEnv('easy_explicit_hate')

# Episode 1
obs1 = env.reset()
action1 = ContentModAction(category='hate_speech', severity=0.8, reasoning='Test', recommended_action='remove')
obs1_step, reward1, done1, info1 = env.step(action1)
score1 = reward1.score

# Reset and Episode 2 with same action
obs2 = env.reset()
action2 = ContentModAction(category='hate_speech', severity=0.8, reasoning='Test', recommended_action='remove')
obs2_step, reward2, done2, info2 = env.step(action2)
score2 = reward2.score

print(f'Same action in different episodes: Score1={score1:.3f}, Score2={score2:.3f}')
print(f'Post IDs different: {obs1.post_id != obs2.post_id}')

# Test observation richness
obs = env.reset()
print(f'Observation fields: {list(obs.model_dump().keys())}')
print(f'Post text length: {len(obs.post_text)} chars')
print(f'Author history available: {obs.author_history_score}')
print(f'Platform context: {obs.platform_context}')
print(f'Goal provided: {obs.goal}')

# Test reward signal granularity
print(f'\n=== REWARD GRANULARITY ===')
test_actions = [
    ContentModAction(category='hate_speech', severity=0.1, reasoning='Low severity', recommended_action='remove'),
    ContentModAction(category='hate_speech', severity=0.5, reasoning='Medium severity', recommended_action='remove'),
    ContentModAction(category='hate_speech', severity=0.9, reasoning='High severity', recommended_action='remove'),
    ContentModAction(category='hate_speech', severity=0.8, reasoning='High severity', recommended_action='warn'),
]

env = ContentModEnv('easy_explicit_hate')
obs = env.reset()
for i, action in enumerate(test_actions):
    obs_step, reward, done, info = env.step(action)
    print(f'Action {i+1}: severity={action.severity}, action={action.recommended_action} → score={reward.score:.3f}')
