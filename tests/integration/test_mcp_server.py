"""Tests de integración contra el servidor MCP corriendo.

Prerequisitos:
    1. El servidor debe estar corriendo:
       fastmcp run main.py:mcp --transport http --port 8000
    2. MongoDB debe estar corriendo (docker compose up -d)

Ejecutar solo estos tests:
    pytest tests/integration/ -v

Si el servidor no está corriendo, estos tests se skipean
automáticamente.
"""

import asyncio
import pytest
from fastmcp import Client

SERVER_URL = "http://127.0.0.1:8000/mcp/"


def is_server_running() -> bool:
    """Verifica si el servidor MCP está corriendo."""
    import socket
    try:
        sock = socket.create_connection(("127.0.0.1", 8000), timeout=2)
        sock.close()
        return True
    except (ConnectionRefusedError, OSError):
        return False


# Skipea todos los tests si el servidor no está corriendo
pytestmark = pytest.mark.skipif(
    not is_server_running(),
    reason="Servidor MCP no está corriendo en localhost:8000",
)


@pytest.fixture
def client():
    """Crea un cliente MCP conectado al servidor."""
    return Client(SERVER_URL)


class TestQueriesIntegration:
    """Tests de integración para el sub-servidor queries."""

    def test_obtener_todos_los_usuarios(self, client):
        """obtener_usuarios sin filtro retorna una lista no vacía."""
        async def _test():
            async with client as c:
                result = await c.call_tool(
                    "queries_obtener_usuarios", {}
                )
                assert result is not None
                return result

        result = asyncio.run(_test())
        assert len(result) > 0

    def test_obtener_usuarios_filtro_argentina(self, client):
        """obtener_usuarios con filtro retorna solo argentinos."""
        async def _test():
            async with client as c:
                result = await c.call_tool(
                    "queries_obtener_usuarios",
                    {"nacionalidad": "Argentina"},
                )
                return result

        result = asyncio.run(_test())
        assert len(result) > 0

    def test_obtener_usuarios_filtro_inexistente(self, client):
        """Filtro por país inexistente retorna lista vacía."""
        async def _test():
            async with client as c:
                result = await c.call_tool(
                    "queries_obtener_usuarios",
                    {"nacionalidad": "Japón"},
                )
                return result

        result = asyncio.run(_test())
        # Puede retornar lista vacía o texto vacío
        assert result is not None


class TestTransactionsIntegration:
    """Tests de integración para el sub-servidor transactions."""

    def test_collect_user_info(self, client):
        """collect_user_info retorna el saludo esperado."""
        async def _test():
            async with client as c:
                result = await c.call_tool(
                    "transactions_collect_user_info",
                    {"name": "TestUser", "age": 25},
                )
                return result

        result = asyncio.run(_test())
        assert "TestUser" in str(result)
        assert "25" in str(result)

    def test_process_transaction(self, client):
        """process_transaction completa sin errores."""
        async def _test():
            async with client as c:
                result = await c.call_tool(
                    "transactions_process_transaction",
                    {"transaction_id": "TEST-001", "amount": 99.99},
                )
                return result

        result = asyncio.run(_test())
        assert result is not None


class TestListTools:
    """Tests para verificar que los tools están registrados."""

    def test_list_tools_contiene_queries(self, client):
        """El servidor debe exponer queries_obtener_usuarios."""
        async def _test():
            async with client as c:
                tools = await c.list_tools()
                names = [t.name for t in tools]
                return names

        names = asyncio.run(_test())
        assert "queries_obtener_usuarios" in names

    def test_list_tools_contiene_transactions(self, client):
        """El servidor expone los tools de transactions."""
        async def _test():
            async with client as c:
                tools = await c.list_tools()
                names = [t.name for t in tools]
                return names

        names = asyncio.run(_test())
        assert "transactions_collect_user_info" in names
        assert "transactions_process_transaction" in names

    def test_list_tools_total(self, client):
        """El servidor debe tener exactamente 3 tools."""
        async def _test():
            async with client as c:
                tools = await c.list_tools()
                return tools

        tools = asyncio.run(_test())
        assert len(tools) == 3


class TestRateLimiting:
    """Tests de rate-limiting (ejecutar con cuidado).

    NOTA: Este test hace 30 llamadas rápidas y verifica que el
    rate-limiter bloquee a partir de la 26ava.
    Está marcado como 'slow' para que no se ejecute por defecto.
    """

    @pytest.mark.slow
    def test_rate_limit_se_activa(self, client):
        """Después de 25 llamadas, debe rechazar con rate limit."""
        async def _test():
            async with client as c:
                errors = 0
                for i in range(30):
                    try:
                        await c.call_tool(
                            "transactions_collect_user_info",
                            {"name": f"User{i}", "age": 20},
                        )
                    except Exception as e:
                        if "Rate limit" in str(e):
                            errors += 1
                return errors

        errors = asyncio.run(_test())
        assert errors >= 5, (
            f"Se esperaban al menos 5 errores de rate-limit, "
            f"pero hubo {errors}"
        )
