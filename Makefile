format:
	uv run ruff check --select I --fix && uv run ruff format

check:
	uv run ruff check

check-fix:
	uv run ruff check --fix && uv run ruff check --select I --fix