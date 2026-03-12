"""Entidad de dominio: Usuario."""

from pydantic import BaseModel


class Usuario(BaseModel):
    """Representa un usuario del sistema.

    Attributes:
        id: Identificador único del usuario.
        nombre: Nombre del usuario.
        apellido: Apellido del usuario.
        nacionalidad: País de origen.
        profesion: Profesión u ocupación.
        fecha_de_nacimiento: Fecha de nacimiento (formato YYYY-MM-DD).
    """

    id: int
    nombre: str
    apellido: str
    nacionalidad: str
    profesion: str
    fecha_de_nacimiento: str
