from mcp.server.fastmcp import FastMCP
import asyncio

# Initialize the MCP server
mcp = FastMCP("Jobber-Automation")

@mcp.tool()
def search_client(search_term: str):
    """Search for a client in Jobber by name, email, or phone."""
    return {"status": "success", "data": "dummy"}

async def debug_discovery():
    # Use list_tools() which is an async method
    tools = await mcp.list_tools()
    print(f"Listing registered tools: {tools}")

if __name__ == "__main__":
    asyncio.run(debug_discovery())
