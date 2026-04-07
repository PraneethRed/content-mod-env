# Content Moderation Environment

A production-grade OpenEnv environment for training AI agents to apply community guidelines in content moderation scenarios.

## Overview

This environment simulates real-world content moderation tasks where AI agents review social media posts and make decisions about policy violations. It includes three difficulty levels:

- **Easy**: Clear hate speech detection
- **Medium**: Passive-aggressive demographic targeting  
- **Hard**: Satirical misinformation edge cases

## Action Space

The action space is defined by `ContentModAction` with the following fields:

- `category` (str): One of "hate_speech", "harassment", "misinformation", "spam", "safe"
- `severity` (float): Severity score between 0.0 and 1.0
- `reasoning` (str): Explanation for the decision (max 500 characters)
- `recommended_action` (str): One of "remove", "warn", "no_action", "escalate"

## Observation Space

The observation space is defined by `ContentModObservation` with the following fields:

- `post_id` (str): Unique identifier for the post
- `post_text` (str): Content of the social media post (max 2000 characters)
- `author_history_score` (float): Author's historical violation score (0.0-1.0)
- `platform_context` (str): Context about the platform/community
- `task_id` (str): Identifier for the current task
- `step_number` (int): Current step within the episode
- `goal` (str): Goal description for the current task

## Tasks

### Easy: Explicit Hate Speech
- **Description**: Clear hate speech with explicit slurs targeting protected groups
- **Difficulty**: Easy
- **Expected Baseline Score**: 0.85+
- **Ground Truth**: category="hate_speech", severity>0.7, recommended_action="remove"

### Medium: Passive-Aggressive Harassment  
- **Description**: Passive-aggressive content targeting demographics without explicit slurs
- **Difficulty**: Medium
- **Expected Baseline Score**: 0.65+
- **Ground Truth**: category="harassment", severity=0.4-0.6, recommended_action="warn"

### Hard: Satirical Misinformation
- **Description**: Satirical content that could be misinformation or protected speech
- **Difficulty**: Hard
- **Expected Baseline Score**: 0.45+
- **Ground Truth**: category="misinformation", severity=0.5-0.7, recommended_action="escalate"

## Baseline Scores

| Model | Easy Task | Medium Task | Hard Task |
|-------|-----------|-------------|-----------|
| Random Baseline | 0.25 | 0.20 | 0.15 |
| Simple Heuristic | 0.60 | 0.45 | 0.30 |
| LLaMA-3.1-8B | 0.85 | 0.70 | 0.55 |

## Installation

```bash
# Clone and navigate to the project
cd my-env

# Install dependencies
uv sync

# Install OpenEnv core
pip install openenv-core
```

## Setup Instructions

1. Copy environment variables:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
HF_TOKEN=your_huggingface_token_here
```

3. Run locally:
```bash
uv run server
```

The server will start on `http://localhost:7860`

## Usage

### Testing the Environment

```bash
# Test reset endpoint
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d '{}'

# Validate the environment
openenv validate
```

### Docker Deployment

```bash
# Build the Docker image
docker build .

# Run the container
docker run -p 7860:7860 my-env
```

## Environment Structure

- **Models**: Pydantic v2 models for actions, observations, and rewards
- **Tasks**: Three difficulty levels with realistic content scenarios
- **Graders**: Deterministic scoring functions with partial credit
- **Environment**: Full OpenEnv interface with proper state management

## API Endpoints

- `POST /reset` - Reset environment with optional task_id
- `POST /step` - Submit action and get next observation/reward
- `GET /state` - Get current environment state

## Security

- All API keys loaded from environment variables
- Input validation with Pydantic models
- No hardcoded secrets
- Proper state isolation between episodes
