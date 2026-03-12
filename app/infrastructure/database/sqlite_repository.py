"""Implementación del repositorio de usuarios con SQLite."""

import sqlite3

from app.domain.entities.usuario import Usuario
from app.domain.interfaces.user_repository import UserRepository


class SqliteUserRepository(UserRepository):
    """Accede a la tabla ``usuarios`` en una base de datos SQLite.

    Attributes:
        db_path: Ruta absoluta al archivo ``.db``.
    """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Crea y retorna una conexión a la base de datos.

        Returns:
            Conexión SQLite con ``row_factory`` configurado.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_all(
        self, nacionalidad: str | None = None
    ) -> list[Usuario]:
        """Retorna usuarios, opcionalmente filtrados por nacionalidad.

        Args:
            nacionalidad: País por el cual filtrar. Si es ``None``
                se retornan todos los registros.

        Returns:
            Lista de entidades ``Usuario``.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if nacionalidad:
            cursor.execute(
                "SELECT * FROM usuarios WHERE nacionalidad = ?",
                (nacionalidad,),
            )
        else:
            cursor.execute("SELECT * FROM usuarios")

        rows = cursor.fetchall()
        conn.close()

        return [
            Usuario(
                id=row["id"],
                nombre=row["nombre"],
                apellido=row["apellido"],
                nacionalidad=row["nacionalidad"],
                profesion=row["profesion"],
                fecha_de_nacimiento=row["fecha_de_nacimiento"],
            )
            for row in rows
        ]
