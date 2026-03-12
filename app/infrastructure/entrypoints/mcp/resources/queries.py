"""Sub-servidor MCP con queries de solo lectura sobre la base de datos.

Este módulo se monta como namespace ``queries`` en el servidor
principal definido en ``main.py``.
"""

import os

from fastmcp import FastMCP

from app.application.use_cases.get_users import GetUsersUseCase
from app.domain.entities.usuario import Usuario
from app.infrastructure.database.sqlite_repository import (
    SqliteUserRepository,
)

queries = FastMCP("queries")

# ---------------------------------------------------------------------------
# Inyección de dependencias
# ---------------------------------------------------------------------------
db_path = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(__file__), "./users.db"),
)

user_repository = SqliteUserRepository(db_path)
get_users_use_case = GetUsersUseCase(user_repository)


@queries.tool()
def obtener_usuarios(
    nacionalidad: str | None = None,
) -> list[Usuario]:
    """Obtiene la lista de usuarios de la base de datos.

    Opcionalmente filtra por nacionalidad.

    Args:
        nacionalidad: País por el cual filtrar (ej. ``Argentina``).

    Returns:
        Lista de objetos ``Usuario``.
    """
    return get_users_use_case.execute(nacionalidad)


@queries.resource("db://usuarios/todos")
def resource_usuarios() -> str:
    """Retorna todos los usuarios como un string formateado."""
    usuarios = get_users_use_case.execute()
    return "\n".join(
        f"{u.id}: {u.nombre} {u.apellido} ({u.profesion})"
        for u in usuarios
    )
