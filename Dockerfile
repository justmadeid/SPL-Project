FROM node:22-bookworm-slim AS frontend-build
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
WORKDIR /app
RUN pip install --no-cache-dir uv==0.12.24
COPY backend/pyproject.toml backend/uv.lock ./backend/
RUN cd backend && uv sync --frozen --no-dev
COPY backend/app ./backend/app
COPY --from=frontend-build /build/frontend/dist ./frontend/dist
ENV PYTHONUNBUFFERED=1 PORT=10000
EXPOSE 10000
CMD ["sh", "-c", "exec backend/.venv/bin/uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-10000}"]
