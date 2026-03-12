"""Punto de entrada principal del servidor MCP.

Configura el servidor FastMCP con tools, middlewares y recursos
montados, y lo ejecuta vía transporte HTTP.
"""

from dotenv import load_dotenv

load_dotenv()

from fastmcp import FastMCP  # noqa: E402

from app.infrastructure.entrypoints.mcp.resources.queries import (  # noqa: E402
    queries,
)
from app.infrastructure.entrypoints.mcp.resources.transactions import (  # noqa: E402
    transactions,
)
from fastmcp.server.middleware.error_handling import (  # noqa: E402
    ErrorHandlingMiddleware,
)
from fastmcp.server.middleware.rate_limiting import (  # noqa: E402
    SlidingWindowRateLimitingMiddleware,
)
from fastmcp.server.middleware.logging import LoggingMiddleware  # noqa: E402
from app.infrastructure.middleware.tool_call_logging_middleware import (  # noqa: E402
    ToolCallLoggingMiddleware,
)
from app.infrastructure.middleware.rate_limit_event_middleware import (  # noqa: E402
    RateLimitEventMiddleware,
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
MAX_REQUESTS_PER_MINUTE = 25
RATE_LIMIT_WINDOW_MINUTES = 1

# ---------------------------------------------------------------------------
# Servidor MCP
# ---------------------------------------------------------------------------
mcp = FastMCP("First MCP Server")

# ---------------------------------------------------------------------------
# Middlewares (orden: último agregado se ejecuta primero)
# ---------------------------------------------------------------------------
mcp.add_middleware(ErrorHandlingMiddleware())
mcp.add_middleware(RateLimitEventMiddleware())
mcp.add_middleware(
    SlidingWindowRateLimitingMiddleware(
        max_requests=MAX_REQUESTS_PER_MINUTE,
        window_minutes=RATE_LIMIT_WINDOW_MINUTES,
    )
)
mcp.add_middleware(LoggingMiddleware())
mcp.add_middleware(ToolCallLoggingMiddleware())

# ---------------------------------------------------------------------------
# Sub-servidores montados como namespaces
# ---------------------------------------------------------------------------
mcp.mount(queries, namespace="queries")
mcp.mount(transactions, namespace="transactions")

if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
