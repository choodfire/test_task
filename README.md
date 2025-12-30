# Тестовое задание

---

## Запуск

* Создать .env на основе .env.example (`cp .env.example .env` достаточно)
* `docker compose up -d --build`
* FastAPI документация доступна на `http://localhost:8000/docs`

### Запуск тестов

* Создать .env.test на основе .env.example
* Указать `DEBUG=True` в .env.test
* Создать базу данных под тесты, указать её в .env.test
* Указать правильно хосты Postgres и RabbitMQ
* Создать очередь RabbitMQ для интеграционных тестов, указать её в .env.test
* `uv sync --frozen`
* `source .venv/bin/activate`
* `pytest`

---

