"""Middleware que registra en MongoDB los eventos de rate-limit excedido."""

from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from fastmcp.server.middleware import Middleware, MiddlewareContext

from app.infrastructure.middleware.mongo_config import (
    rate_limit_collection,
)


class RateLimitEventMiddleware(Middleware):
    """Captura excepciones de rate-limit y las persiste en MongoDB.

    Los documentos se almacenan en
    ``mcp_logs.rate_limit_exceeded``.
    La excepción se re-lanza para que el middleware de
    rate-limiting upstream la maneje.
    """

    async def on_call_tool(
        self,
        context: MiddlewareContext,
        call_next: Callable[..., Any],
    ) -> Any:
        """Intercepta errores de rate-limit y los registra.

        Args:
            context: Contexto del middleware con información de la
                solicitud MCP.
            call_next: Siguiente middleware en la cadena.

        Raises:
            Exception: Re-lanza cualquier excepción capturada
                después de registrarla.
        """
        try:
            return await call_next(context)
        except Exception as exc:
            await rate_limit_collection.insert_one({
                "tool_name": context.message.name,
                "arguments": dict(
                    context.message.arguments or {}
                ),
                "session_id": (
                    context.fastmcp_context.session_id
                ),
                "timestamp": datetime.now(timezone.utc),
                "error": str(exc),
            })
            raise
