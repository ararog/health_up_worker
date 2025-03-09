# Install uv
FROM python:3.12-slim AS base

FROM base as builder

RUN apt-get update &&  \
  apt-get install -y libpq-dev gcc

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project --no-editable

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-editable


FROM base AS test
RUN echo "nothing to do"


FROM base AS runtime

RUN apt-get update &&  \
  apt-get install -y libpq-dev gcc && \
  rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=app:app /app /app

WORKDIR /app

CMD ["uv", "run", "main.py"]