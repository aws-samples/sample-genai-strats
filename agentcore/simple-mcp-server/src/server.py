import os

from mcp.server import MCPServer
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

mcp = MCPServer("simple-mcp-server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers.""" 
    return a + b


@mcp.prompt(title="Code review")
def review_code(code: str, language: str = "python") -> str:
    """Ask the model to review a piece of code."""
    return f"Please review this {language} code:\n\n{code}"


@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=8000,
        stateless_http=True,
        json_response=True,
    )
