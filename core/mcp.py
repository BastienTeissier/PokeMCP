from fastmcp import FastMCP

mcp = FastMCP("pokedex")

# Create the ASGI app
mcp_app = mcp.http_app(path="/")
