format:
	uv run ruff check --select I --fix && uv run ruff format

check:
	uv run ruff check

check-fix:
	uv run ruff check --fix && uv run ruff check --select I --fix

start_fast_mcp:
	uv run main.py

start-api:
	uv run fastapi dev api.py

inspector:
	npx @modelcontextprotocol/inspector