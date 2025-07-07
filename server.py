import uvicorn
from fastapi import FastAPI

from core.mcp import mcp_app

# Create a FastAPI app and mount the MCP server
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
