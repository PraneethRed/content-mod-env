#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_mod_env.env import ContentModEnv

# Test static data check
print('=== TESTING STATIC DATA CHECK ===')

env = ContentModEnv('easy_explicit_hate')

# Call reset() 3 times - observations should vary
obs1 = env.reset()
obs2 = env.reset() 
obs3 = env.reset()

print(f'Reset 1 post_id: {obs1.post_id}')
print(f'Reset 2 post_id: {obs2.post_id}')
print(f'Reset 3 post_id: {obs3.post_id}')

# Check post_id uniqueness
post_ids = [obs1.post_id, obs2.post_id, obs3.post_id]
assert len(set(post_ids)) == 3, 'post_id should be unique per episode'
print('✅ post_id uniqueness verified')

# Check step_number increments within an episode
env = ContentModEnv('easy_explicit_hate')
obs_start = env.reset()
print(f'Step number at start: {obs_start.step_number}')

from content_mod_env.models import ContentModAction
action = ContentModAction(
    category="hate_speech",
    severity=0.8,
    reasoning="Test",
    recommended_action="remove"
)

obs_step, reward, done, info = env.step(action)
print(f'Step number after step: {obs_step.step_number}')

assert obs_step.step_number == obs_start.step_number + 1, 'step_number should increment'
print('✅ step_number increment verified')

# Check task cycling or randomization exists
posts = []
for i in range(5):
    obs = env.reset()
    posts.append(obs.post_text)

unique_posts = set(posts)
print(f'Unique posts from 5 resets: {len(unique_posts)}')
assert len(unique_posts) > 1, 'Should have multiple different posts'
print('✅ Post variation verified')

print('✅ Static data check passed')
