"""Interfaz abstracta del repositorio de usuarios."""

from abc import ABC, abstractmethod

from app.domain.entities.usuario import Usuario


class UserRepository(ABC):
    """Contrato que deben cumplir las implementaciones de repositorio.

    Define las operaciones de lectura sobre la entidad ``Usuario``.
    """

    @abstractmethod
    def get_all(
        self, nacionalidad: str | None = None
    ) -> list[Usuario]:
        """Retorna la lista de usuarios, opcionalmente filtrada.

        Args:
            nacionalidad: Si se indica, filtra usuarios por
                nacionalidad.

        Returns:
            Lista de entidades ``Usuario``.
        """
