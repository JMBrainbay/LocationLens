# syntax=docker/dockerfile:1.7

FROM python:3.12-slim AS api
WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir \
      fastapi \
      httpx \
      pydantic \
      pydantic-settings \
      uvicorn \
      eval_type_backport

COPY apps/api/src /app/apps/api/src
COPY apps/api/pyproject.toml /app/apps/api/pyproject.toml

WORKDIR /app/apps/api
ENV PYTHONPATH=/app/apps/api/src
EXPOSE 4000
CMD ["python", "-m", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "4000"]


FROM node:20-alpine AS web
WORKDIR /app
RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml /app/
COPY apps/web/package.json /app/apps/web/package.json
COPY packages/contracts/package.json /app/packages/contracts/package.json

RUN corepack pnpm install --frozen-lockfile

COPY apps/web /app/apps/web
COPY packages/contracts /app/packages/contracts

WORKDIR /app/apps/web
EXPOSE 3000
CMD ["corepack", "pnpm", "exec", "next", "dev", "-p", "3000", "-H", "0.0.0.0"]
