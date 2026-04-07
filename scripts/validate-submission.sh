#!/bin/bash

echo "Validating Content Moderation Environment submission..."

# Check if required files exist
required_files=(
    "inference.py"
    "Dockerfile"
    "openenv.yaml"
    "README.md"
    ".env.example"
    ".gitignore"
    "pyproject.toml"
    "src/content_mod_env/__init__.py"
    "src/content_mod_env/env.py"
    "src/content_mod_env/models.py"
    "src/content_mod_env/tasks/__init__.py"
    "src/content_mod_env/tasks/task_easy.py"
    "src/content_mod_env/tasks/task_medium.py"
    "src/content_mod_env/tasks/task_hard.py"
    "src/content_mod_env/graders/__init__.py"
    "src/content_mod_env/graders/grader_easy.py"
    "src/content_mod_env/graders/grader_medium.py"
    "src/content_mod_env/graders/grader_hard.py"
)

echo "Checking required files..."
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file missing"
        exit 1
    fi
done

# Check if .env is in .gitignore
if grep -q "^\.env$" .gitignore; then
    echo "✓ .env is in .gitignore"
else
    echo "✗ .env not found in .gitignore"
    exit 1
fi

# Check for hardcoded secrets
echo "Checking for hardcoded secrets..."
if grep -rE "(hf_token|api_key|secret|password|token)" --include="*.py" src/ inference.py | grep -v "post_text\|author_history_score\|platform_context\|API_KEY\|max_tokens"; then
    echo "✗ Potential hardcoded secrets found"
    exit 1
else
    echo "✓ No hardcoded secrets detected"
fi

# Check pyproject.toml structure
echo "Checking pyproject.toml..."
if python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))" 2>/dev/null; then
    echo "✓ pyproject.toml is valid"
else
    echo "✗ pyproject.toml is invalid"
    exit 1
fi

# Check openenv.yaml structure  
echo "Checking openenv.yaml..."
if python -c "import yaml; yaml.safe_load(open('openenv.yaml'))" 2>/dev/null; then
    echo "✓ openenv.yaml is valid"
else
    echo "✗ openenv.yaml is invalid"
    exit 1
fi

echo "Validation complete! ✓"
