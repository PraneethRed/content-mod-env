---
title: Content Mod Env
emoji: 🛡️
colorFrom: blue
colorTo: yellow
sdk: docker
app_port: 7860
pinned: false
---

# Content Moderation Environment

An OpenEnv-compatible reinforcement learning environment where AI agents learn to apply community guidelines to social media content — the same core problem Meta's Trust & Safety teams solve at billion-user scale.

## Why This Problem

Content moderation is one of the hardest real-world AI challenges:
- Context is everything — the same words mean different things in different communities
- Edge cases are endless — satire, passive aggression, coordinated inauthentic behavior
- Stakes are high — wrong calls harm real people or suppress legitimate speech
- Scale is impossible for humans alone — billions of posts per day

This environment trains agents to make these judgment calls reliably.

## Environment Design

The agent receives a social media post with contextual signals and must decide:
- **What policy was violated** (category)
- **How severe the violation is** (severity 0.0–1.0)
- **What action to take** (remove / warn / escalate / no_action)
- **Why** (reasoning, used for grader quality scoring)

### Observation Space
| Field | Type | Description |
|---|---|---|
| post_text | string | The social media post content |
| author_history_score | float | Author's prior violation history (0.0–1.0) |
| platform_context | string | Where the post appeared (general, groups, marketplace) |
| task_id | string | Which moderation scenario is active |
| goal | string | Natural language description of what to detect |

### Action Space
| Field | Type | Description |
|---|---|---|
| category | enum | hate_speech / harassment / misinformation / spam / safe |
| severity | float | 0.0 (mild) to 1.0 (extreme) |
| recommended_action | enum | remove / warn / escalate / no_action |
| reasoning | string | Agent's justification (max 500 chars) |

### Reward Structure
| Component | Weight | Description |
|---|---|---|
| Category match | 0.40 | Correct violation type identified |
| Severity accuracy | 0.30 | How close severity is to ground truth |
| Action match | 0.20 | Correct enforcement action |
| Reasoning quality | 0.10 | Length and policy keyword usage |

## Tasks

### 🟢 Easy — Explicit Hate Speech (`easy_explicit_hate`)
Clear, unambiguous hate speech targeting ethnic groups. Tests baseline detection.
- Ground truth: `category=hate_speech`, `severity>0.7`, `action=remove`
- Typical agent score: 0.80+

### 🟡 Medium — Passive Harassment (`medium_passive_harassment`)
Passive-aggressive demographic targeting — no slurs, but clear intent to demean.
Tests nuanced understanding beyond keyword matching.
- Ground truth: `category=harassment`, `severity=0.4–0.6`, `action=warn`
- Typical agent score: 0.70+

### 🔴 Hard — Satire vs Misinformation (`hard_satire_misinformation`)
Satirical news-style content that spreads false information. The hardest real-world
moderation edge case — even human moderators disagree on these.
- Ground truth: `category=misinformation`, `severity=0.5–0.7`, `action=escalate`
- Typical agent score: 0.75+

## API Endpoints
POST /reset   — Start a new episode, returns first observation
POST /step    — Submit an action, returns reward + next observation
GET  /state   — Current environment state
GET  /health  — Health check

### Quick Start

```bash
# Reset environment
curl -X POST https://praneethred-content-mod-env.hf.space/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "easy_explicit_hate"}'

# Submit an action
curl -X POST https://praneethred-content-mod-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "easy_explicit_hate",
    "action": {
      "category": "hate_speech",
      "severity": 0.85,
      "reasoning": "Post contains explicit ethnic slurs and dehumanizing language targeting a protected group",
      "recommended_action": "remove"
    }
  }'
```

## Stack

- **Python 3.11** — core runtime
- **FastAPI** — environment API server
- **Pydantic v2** — action/observation validation
- **OpenAI client** — LLM inference via HuggingFace router
- **Docker** — containerized deployment
- **openenv-core** — OpenEnv spec compliance

## Agent Performance (Llama-3.1-8B-Instruct)

| Task | Score |
|---|---|
| easy_explicit_hate | 0.81 |
| medium_passive_harassment | 0.93 |
| hard_satire_misinformation | 0.85 |

## Project Structure
content-mod-env/
├── inference.py              # Agent client — runs the LLM agent loop
├── app.py                    # FastAPI server — environment API
├── openenv.yaml              # OpenEnv spec
├── Dockerfile
└── src/
└── content_mod_env/
├── env.py            # Environment logic + reward computation
├── models.py         # Pydantic v2 models
├── tasks/            # Task definitions (easy/medium/hard)
└── graders/          # Per-task grading logic

## Design Decisions

**Why content moderation?** It's one of the few domains where the gap between rule-based systems and contextual AI judgment is enormous and well-documented. An RL environment here has direct real-world value.

**Why three difficulty tiers?** Moderation difficulty isn't binary. Easy cases (slurs) are handled well by classifiers. The hard cases (satire, passive aggression) are where human moderators spend most of their time — and where AI agents need the most training.

**Why escalate for satire?** Satirical misinformation is the hardest call in content moderation. Rather than auto-remove (suppresses legitimate speech) or ignore (spreads false info), escalating to human review reflects actual best practice used by major platforms.

**Grader design:** Rewards are decomposed into independent components so agents learn which part of their decision was wrong. A single scalar reward would not teach an agent whether it got the category wrong, the severity wrong, or the action wrong.
