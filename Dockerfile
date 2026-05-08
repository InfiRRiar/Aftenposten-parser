FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates bash \
    && rm -rf /var/lib/apt/lists/*

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
ENV UV_NO_DEV=1

COPY ./uv.lock pyproject.toml /app/
RUN uv sync --locked
RUN uv run playwright install --with-deps

COPY cookies.json .env settings.py /app/
COPY src/disk_loader.py src/main.py /app/src/

ENV PATH="/app/.venv/bin:$PATH"
CMD ["uv", "run", "python", "-m", "src.main"]
