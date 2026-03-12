"""Fixtures compartidos para toda la suite de tests."""

import pytest
from app.domain.entities.usuario import Usuario
from app.infrastructure.database.sqlite_repository import (
    SqliteUserRepository,
)
from app.application.use_cases.get_users import GetUsersUseCase


@pytest.fixture
def sample_usuario() -> Usuario:
    """Retorna un usuario de ejemplo para tests."""
    return Usuario(
        id=1,
        nombre="Juan",
        apellido="Perez",
        nacionalidad="Argentina",
        profesion="Programador",
        fecha_de_nacimiento="1990-05-15",
    )


@pytest.fixture
def sample_usuarios() -> list[Usuario]:
    """Retorna una lista de usuarios de ejemplo para tests."""
    return [
        Usuario(
            id=1, nombre="Juan", apellido="Perez",
            nacionalidad="Argentina", profesion="Programador",
            fecha_de_nacimiento="1990-05-15",
        ),
        Usuario(
            id=2, nombre="Maria", apellido="Lopez",
            nacionalidad="Chile", profesion="Ingeniero",
            fecha_de_nacimiento="1985-08-20",
        ),
        Usuario(
            id=3, nombre="Carlos", apellido="Garcia",
            nacionalidad="Argentina", profesion="Médico",
            fecha_de_nacimiento="1978-12-01",
        ),
    ]


@pytest.fixture
def sqlite_repo(tmp_path) -> SqliteUserRepository:
    """Crea un repositorio SQLite temporal con datos de prueba."""
    import sqlite3

    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            nacionalidad TEXT NOT NULL,
            profesion TEXT NOT NULL,
            fecha_de_nacimiento DATE NOT NULL
        )
    """)

    test_data = [
        ("Juan", "Perez", "Argentina", "Programador", "1990-05-15"),
        ("Maria", "Lopez", "Chile", "Ingeniero", "1985-08-20"),
        ("Carlos", "Garcia", "Argentina", "Médico", "1978-12-01"),
        ("Ana", "Torres", "México", "Docente", "1992-03-10"),
    ]

    cursor.executemany(
        "INSERT INTO usuarios "
        "(nombre, apellido, nacionalidad, profesion, fecha_de_nacimiento) "
        "VALUES (?, ?, ?, ?, ?)",
        test_data,
    )

    conn.commit()
    conn.close()

    return SqliteUserRepository(db_path)


@pytest.fixture
def get_users_use_case(sqlite_repo) -> GetUsersUseCase:
    """Retorna un caso de uso conectado a la DB temporal."""
    return GetUsersUseCase(sqlite_repo)
