FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache

COPY . .

EXPOSE 8080

# CMD ["uv", "run", "agent.py"]
CMD ["uv", "run", "opentelemetry-instrument", "python", "agent.py"]
