"""Tests unitarios para la entidad Usuario."""

import pytest
from pydantic import ValidationError
from app.domain.entities.usuario import Usuario


class TestUsuarioEntity:
    """Valida la creación y validación de la entidad Usuario."""

    def test_crear_usuario_valido(self, sample_usuario):
        """Un usuario con todos los campos válidos se crea sin error."""
        assert sample_usuario.nombre == "Juan"
        assert sample_usuario.apellido == "Perez"
        assert sample_usuario.nacionalidad == "Argentina"
        assert sample_usuario.profesion == "Programador"
        assert sample_usuario.fecha_de_nacimiento == "1990-05-15"

    def test_usuario_tiene_id(self, sample_usuario):
        """El ID debe ser un entero."""
        assert isinstance(sample_usuario.id, int)
        assert sample_usuario.id == 1

    def test_usuario_requiere_campos_obligatorios(self):
        """Pydantic debe rechazar la creación sin campos requeridos."""
        with pytest.raises(ValidationError):
            Usuario()  # type: ignore

    def test_usuario_rechaza_id_invalido(self):
        """Pydantic debe rechazar un ID no entero."""
        with pytest.raises(ValidationError):
            Usuario(
                id="abc",  # type: ignore
                nombre="Test",
                apellido="Test",
                nacionalidad="Test",
                profesion="Test",
                fecha_de_nacimiento="2000-01-01",
            )

    def test_usuario_serializa_a_dict(self, sample_usuario):
        """model_dump() debe retornar un diccionario con todos los campos."""
        data = sample_usuario.model_dump()
        assert isinstance(data, dict)
        assert data["nombre"] == "Juan"
        assert "id" in data
        assert len(data) == 6

    def test_usuario_serializa_a_json(self, sample_usuario):
        """model_dump_json() debe retornar un string JSON válido."""
        json_str = sample_usuario.model_dump_json()
        assert isinstance(json_str, str)
        assert '"nombre":"Juan"' in json_str
