"""Caso de uso: obtener usuarios del sistema."""

from app.domain.entities.usuario import Usuario
from app.domain.interfaces.user_repository import UserRepository


class GetUsersUseCase:
    """Orquesta la obtención de usuarios a través del repositorio.

    Attributes:
        user_repository: Implementación concreta del repositorio.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def execute(
        self, nacionalidad: str | None = None
    ) -> list[Usuario]:
        """Ejecuta la consulta de usuarios.

        Args:
            nacionalidad: Filtro opcional por país de origen.

        Returns:
            Lista de entidades ``Usuario``.
        """
        return self.user_repository.get_all(nacionalidad)
