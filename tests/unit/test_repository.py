"""Tests unitarios para el repositorio SQLite."""

import pytest
from app.domain.entities.usuario import Usuario


class TestSqliteUserRepository:
    """Tests del repositorio usando una DB SQLite temporal."""

    def test_get_all_retorna_lista(self, sqlite_repo):
        """get_all() debe retornar una lista no vacía."""
        result = sqlite_repo.get_all()
        assert isinstance(result, list)
        assert len(result) == 4

    def test_get_all_retorna_usuarios(self, sqlite_repo):
        """Cada elemento debe ser una instancia de Usuario."""
        result = sqlite_repo.get_all()
        for usuario in result:
            assert isinstance(usuario, Usuario)

    def test_get_all_sin_filtro(self, sqlite_repo):
        """Sin filtro, retorna todos los usuarios."""
        result = sqlite_repo.get_all()
        assert len(result) == 4

    def test_get_all_filtro_argentina(self, sqlite_repo):
        """Filtrar por 'Argentina' retorna solo argentinos."""
        result = sqlite_repo.get_all(nacionalidad="Argentina")
        assert len(result) == 2
        for u in result:
            assert u.nacionalidad == "Argentina"

    def test_get_all_filtro_chile(self, sqlite_repo):
        """Filtrar por 'Chile' retorna solo chilenos."""
        result = sqlite_repo.get_all(nacionalidad="Chile")
        assert len(result) == 1
        assert result[0].nombre == "Maria"

    def test_get_all_filtro_sin_resultados(self, sqlite_repo):
        """Filtrar por un país inexistente retorna lista vacía."""
        result = sqlite_repo.get_all(nacionalidad="Japón")
        assert result == []

    def test_get_all_filtro_none(self, sqlite_repo):
        """Filtrar con None retorna todos (equivale a sin filtro)."""
        result = sqlite_repo.get_all(nacionalidad=None)
        assert len(result) == 4

    def test_usuario_tiene_todos_los_campos(self, sqlite_repo):
        """Cada usuario debe tener todos los campos completos."""
        result = sqlite_repo.get_all()
        usuario = result[0]
        assert usuario.id is not None
        assert usuario.nombre != ""
        assert usuario.apellido != ""
        assert usuario.nacionalidad != ""
        assert usuario.profesion != ""
        assert usuario.fecha_de_nacimiento != ""
