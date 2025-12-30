run:
	uv run main.py

check-lint:
	ruff check . && ruff format --check

fix-lint:
	ruff format && ruff check --fix
