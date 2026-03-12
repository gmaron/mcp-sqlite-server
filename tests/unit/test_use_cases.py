"""Tests unitarios para el caso de uso GetUsersUseCase."""

import pytest
from unittest.mock import MagicMock
from app.application.use_cases.get_users import GetUsersUseCase
from app.domain.entities.usuario import Usuario
from app.domain.interfaces.user_repository import UserRepository


class TestGetUsersUseCase:
    """Tests del caso de uso con repository real (DB temporal)."""

    def test_execute_retorna_todos(self, get_users_use_case):
        """execute() sin filtro retorna todos los usuarios."""
        result = get_users_use_case.execute()
        assert len(result) == 4

    def test_execute_con_filtro(self, get_users_use_case):
        """execute() con nacionalidad filtra correctamente."""
        result = get_users_use_case.execute(nacionalidad="Argentina")
        assert len(result) == 2

    def test_execute_retorna_tipo_correcto(self, get_users_use_case):
        """execute() retorna una lista de Usuario."""
        result = get_users_use_case.execute()
        assert isinstance(result, list)
        assert all(isinstance(u, Usuario) for u in result)


class TestGetUsersUseCaseWithMock:
    """Tests del caso de uso con mock del repositorio."""

    def test_execute_llama_get_all(self):
        """execute() debe delegar en repository.get_all()."""
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_all.return_value = []

        use_case = GetUsersUseCase(mock_repo)
        use_case.execute()

        mock_repo.get_all.assert_called_once_with(None)

    def test_execute_pasa_nacionalidad_al_repo(self):
        """execute() pasa el parámetro nacionalidad al repo."""
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_all.return_value = []

        use_case = GetUsersUseCase(mock_repo)
        use_case.execute(nacionalidad="Chile")

        mock_repo.get_all.assert_called_once_with("Chile")

    def test_execute_retorna_lo_que_devuelve_el_repo(
        self, sample_usuarios
    ):
        """execute() retorna exactamente lo que retorna el repo."""
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.get_all.return_value = sample_usuarios

        use_case = GetUsersUseCase(mock_repo)
        result = use_case.execute()

        assert result == sample_usuarios
        assert len(result) == 3
