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

COPY package.json package-lock.json ./
COPY apps/web/package.json apps/web/
COPY packages/contracts/package.json packages/contracts/
COPY apps/api/package.json apps/api/

RUN npm ci

COPY apps/web apps/web
COPY packages/contracts packages/contracts

WORKDIR /app
EXPOSE 3000
CMD ["npm", "run", "dev", "-w", "@nl-location-lens/web", "--", "-H", "0.0.0.0"]
