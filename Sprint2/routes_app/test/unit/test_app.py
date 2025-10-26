# test/unit/test_app.py
import pytest
from unittest.mock import patch, MagicMock
from src.models.route import Route


@pytest.mark.unit
class TestApp:
    """Pruebas unitarias para la aplicación Flask"""

    def test_create_app_returns_flask_instance(self):
        """Test que create_app retorna una instancia de Flask"""
        from src.app import create_app

        app = create_app()
        from flask import Flask

        assert isinstance(app, Flask)

    def test_app_has_testing_config(self, app):
        """Test que la app tiene configuración de testing"""
        assert app.config["TESTING"] is True

    def test_app_creates_database_tables(self, app):
        """Test que la app crea las tablas de la base de datos"""
        # En nuestro fixture, las tablas se crean
        from src.models.route import Base

        # Verificar que Base tiene metadatos configurados
        assert Base.metadata is not None
        assert len(Base.metadata.tables) > 0

    def test_app_registers_routes_blueprint(self, app):
        """Test que la app registra el blueprint de rutas"""
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert "routes" in blueprint_names

    def test_app_has_teardown_handler(self, app):
        """Test que la app tiene un manejador de teardown"""
        assert len(app.teardown_appcontext_funcs) > 0

    @patch("src.app.SessionLocal")
    def test_teardown_handler_removes_session(self, mock_session, app):
        """Test que el teardown handler limpia la sesión"""
        # Reset the mock to start fresh
        mock_session.reset_mock()

        # Simular el teardown
        with app.app_context():
            teardown_func = app.teardown_appcontext_funcs[0]
            teardown_func(None)

        # Verificar que remove fue llamado al menos una vez
        mock_session.remove.assert_called()

    @patch("src.app.SessionLocal")
    def test_teardown_handler_handles_exceptions(self, mock_session, app):
        """Test que el teardown handler maneja excepciones"""
        mock_session.remove.side_effect = Exception("Session error")

        # No debería lanzar excepción
        with app.app_context():
            teardown_func = app.teardown_appcontext_funcs[0]
            teardown_func(None)


@pytest.mark.unit
class TestAppEndpoints:
    """Pruebas unitarias para endpoints de la aplicación"""

    def test_ping_endpoint_exists(self, client):
        """Test que existe el endpoint /routes/ping"""
        response = client.get("/routes/ping")
        assert response.status_code == 200

    def test_ping_endpoint_returns_pong(self, client):
        """Test que /routes/ping retorna 'pong'"""
        response = client.get("/routes/ping")
        assert response.data == b"pong"
        assert response.content_type == "text/plain; charset=utf-8"

    @patch("src.app.SessionLocal")
    def test_reset_endpoint_exists(self, mock_session, client):
        """Test que existe el endpoint /routes/reset"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        # Añadir mock para la llamada a query().delete() que ocurre en el endpoint
        mock_db.query.return_value.delete.return_value = 0

        response = client.post("/routes/reset")
        assert response.status_code == 200
    @patch("src.app.SessionLocal")
    def test_reset_endpoint_deletes_routes(self, mock_session, client):
        """Test que /routes/reset elimina todas las rutas"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.delete.return_value = 1

        response = client.post("/routes/reset")

        assert response.status_code == 200
        data = response.get_json()
        assert data["msg"] == "Todos los datos fueron eliminados"

        # verificar que query fue llamada con una clase llamada 'Route'
        assert mock_db.query.call_count == 1
        called_arg = mock_db.query.call_args[0][0]
        assert getattr(called_arg, "__name__", "") == "Route"
        mock_query.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("src.app.SessionLocal")
    def test_routes_reset_endpoint_exists(self, mock_session, client):
        """Test que existe el endpoint /routes/reset (verificación duplicada)"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_db.query.return_value.delete.return_value = 0

        response = client.post("/routes/reset")
        assert response.status_code == 200

    @patch("src.app.SessionLocal")
    def test_routes_reset_endpoint_deletes_routes(self, mock_session, client):
        """Test que /routes/reset elimina todas las rutas (verificación duplicada)"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.delete.return_value = 1

        response = client.post("/routes/reset")

        assert response.status_code == 200
        data = response.get_json()
        assert data["msg"] == "Todos los datos fueron eliminados"

        # verificar que query fue llamada con una clase llamada 'Route'
        assert mock_db.query.call_count == 1
        called_arg = mock_db.query.call_args[0][0]
        assert getattr(called_arg, "__name__", "") == "Route"
        mock_query.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("src.app.SessionLocal")
    def test_reset_endpoint_closes_session(self, mock_session, client):
        """Test que los endpoints de reset cierran la sesión"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db

        client.post("/routes/reset")
        mock_db.close.assert_called_once()
