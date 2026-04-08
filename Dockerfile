FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN pip install uv && uv sync --no-dev

COPY . .

RUN pip install openenv-core

EXPOSE 7860

CMD ["python", "inference.py"]
