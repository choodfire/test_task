FROM python:3.11.7-slim-bookworm

RUN pip install uv

WORKDIR /app

COPY uv.lock pyproject.toml ./

RUN uv sync --frozen

COPY . .

ENTRYPOINT ["./entrypoint"]

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
