"""Middleware que registra cada llamada a tool en MongoDB."""

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext

from app.infrastructure.middleware.mongo_config import (
    tool_calls_collection,
)


class ToolCallLoggingMiddleware(Middleware):
    """Persiste un documento por cada invocación a un tool MCP.

    Los documentos se almacenan en la colección
    ``mcp_logs.tool_calls`` e incluyen nombre del tool, argumentos,
    duración y resultado.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext,
        call_next: Callable[..., Any],
    ) -> Any:
        """Intercepta la llamada al tool y registra el resultado.

        Args:
            context: Contexto del middleware con información de la
                solicitud MCP.
            call_next: Siguiente middleware en la cadena.

        Returns:
            El resultado del tool, sin modificarlo.
        """
        start = datetime.now(timezone.utc)
        error: str | None = None
        result: Any = None

        try:
            result = await call_next(context)
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            msg = context.message
            elapsed_ms = (datetime.now(timezone.utc) - start).total_seconds() * 1000

            await tool_calls_collection.insert_one(
                {
                    "tool_name": msg.name,
                    "arguments": dict(msg.arguments or {}),
                    "method": context.method,
                    "session_id": (
                        context.fastmcp_context.session_id
                        if context.fastmcp_context
                        else None
                    ),
                    "request_id": (
                        context.fastmcp_context.request_id
                        if context.fastmcp_context
                        else None
                    ),
                    "duration_ms": elapsed_ms,
                    "timestamp": start,
                    "status": "error" if error else "ok",
                    "error": error,
                    "result": str(result) if result else None,
                }
            )

        return result
