#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from content_mod_env.env import ContentModEnv

# Test state isolation
print('=== TESTING STATE ISOLATION ===')

env1 = ContentModEnv('easy_explicit_hate')
obs1 = env1.reset()
state1 = env1.state()
print(f'First env - episode_count: {state1["episode_count"]}')

env2 = ContentModEnv('easy_explicit_hate') 
obs2 = env2.reset()
state2 = env2.state()
print(f'Second env - episode_count: {state2["episode_count"]}')

# Test reset() twice produces independent state
env = ContentModEnv('easy_explicit_hate')
obs_first = env.reset()
state_first = env.state()
print(f'First reset - episode_count: {state_first["episode_count"]}')

obs_second = env.reset()
state_second = env.state()
print(f'Second reset - episode_count: {state_second["episode_count"]}')

assert obs_first.post_id != obs_second.post_id, 'post_id should be unique per reset'
assert state_second['episode_count'] == state_first['episode_count'] + 1, 'episode_count should increment on reset'
print('✅ State isolation tests passed')

# Test OpenEnv interface compliance
print('\n=== TESTING OPENENV INTERFACE ===')

env = ContentModEnv('easy_explicit_hate')

# Test reset() signature
obs = env.reset()
print(f'reset() returns: {type(obs).__name__}')

# Test step() signature  
from content_mod_env.models import ContentModAction
action = ContentModAction(
    category="hate_speech",
    severity=0.8,
    reasoning="Test",
    recommended_action="remove"
)
obs, reward, done, info = env.step(action)
print(f'step() returns: {type(obs).__name__}, {type(reward).__name__}, {type(done).__name__}, {type(info).__name__}')

# Test state() signature
state = env.state()
print(f'state() returns: {type(state).__name__}')

print('✅ OpenEnv interface tests passed')
