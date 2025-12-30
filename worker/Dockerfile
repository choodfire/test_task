FROM python:3.11.7-slim-bookworm

ENV UV_SYSTEM_PYTHON=1
ENV PYTHONUNBUFFERED=1

RUN pip install uv

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN uv sync --frozen

COPY . .

CMD ["uv", "run", "python", "-m", "worker.main"]
