format:
	uv run ruff check --select I --fix && uv run ruff format

check:
	uv run ruff check

check-fix:
	uv run ruff check --fix && uv run ruff check --select I --fix

start_fast_mcp:
	uv run main.py

start_fast_mcp_auth:
	uv run main.py --auth --transport sse --port 9999

start-api:
	uv run fastapi dev api.py

test-auth:
	uv run test_auth.py

client:
	uv run client.py

inspector:
	npx @modelcontextprotocol/inspector