# PokeMCP

A Pokemon MCP (Model Context Protocol) server with Supabase authentication integration.

## Features

- 🔥 **Pokemon Data Tools**: Fetch Pokemon information, type effectiveness, and weaknesses
- 🔐 **Supabase Authentication**: Secure user authentication with JWT tokens
- 🤖 **AI-Powered Chat**: Interact with Pokemon data through natural language
- 🚀 **FastMCP Integration**: Built on FastMCP for high performance
- 🎯 **Multiple Transports**: Support for stdio and SSE (Server-Sent Events)

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
