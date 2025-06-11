# PokeMCP

## Installation

1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Start your MCP server:
   ```bash
   uv run main.py
   ```


## Usage
Connect it to a MPC client (Claude Desktop, Copilot, Cursor...) using the following command inside the MCP server :
```bash
/path/to/uv --directory /path/to/mcp run main.py
```
