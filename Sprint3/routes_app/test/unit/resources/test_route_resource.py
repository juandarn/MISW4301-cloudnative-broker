# test/unit/resources/test_route_resource.py
import pytest
import json
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestRouteResource:
    """Pruebas unitarias para los endpoints de rutas"""

    def test_ping_routes(self, client):
        """Test del endpoint /routes/ping"""
        response = client.get("/routes/ping")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "pong"
        assert response.content_type == "text/plain; charset=utf-8"

    @patch("resources.route.SessionLocal")
    def test_create_route_success(self, mock_session, client, sample_route_data):
        """Test de creación exitosa de ruta"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_scalar = MagicMock()
        mock_scalar.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_scalar

        response = client.post(
            "/routes",
            data=json.dumps(sample_route_data),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.get_json()
        assert "id" in data
        assert "createdAt" in data
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_create_route_missing_fields(self, client):
        """Test de creación con campos faltantes"""
        incomplete_data = {
            "flightId": "FL001",
            "sourceAirportCode": "BOG",
        }
        response = client.post(
            "/routes", data=json.dumps(incomplete_data), content_type="application/json"
        )
        assert response.status_code == 400

    def test_create_route_invalid_json(self, client):
        """Test de creación con JSON inválido"""
        response = client.post(
            "/routes", data="invalid-json", content_type="application/json"
        )
        assert response.status_code == 400

    def test_create_route_no_json(self, client):
        """Test de creación sin JSON"""
        response = client.post("/routes")
        assert response.status_code == 400

    @patch("resources.route.SessionLocal")
    def test_create_route_invalid_dates(self, mock_session, client):
        """Test de creación con fechas inválidas"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        invalid_data = {
            "flightId": "FL001",
            "sourceAirportCode": "BOG",
            "sourceCountry": "Colombia",
            "destinyAirportCode": "MDE",
            "destinyCountry": "Colombia",
            "bagCost": 25000,
            "plannedStartDate": "invalid-date",
            "plannedEndDate": "2025-08-25T12:00:00",
        }
        response = client.post(
            "/routes", data=json.dumps(invalid_data), content_type="application/json"
        )
        assert response.status_code == 412
        data = response.get_json()
        assert data["msg"] == "Las fechas del trayecto no son válidas"

    @patch("resources.route.SessionLocal")
    def test_create_route_past_date(self, mock_session, client):
        """Test de creación con fecha en el pasado"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        past_data = {
            "flightId": "FL001",
            "sourceAirportCode": "BOG",
            "sourceCountry": "Colombia",
            "destinyAirportCode": "MDE",
            "destinyCountry": "Colombia",
            "bagCost": 25000,
            "plannedStartDate": "2020-01-01T10:00:00",
            "plannedEndDate": "2020-01-01T12:00:00",
        }
        response = client.post(
            "/routes", data=json.dumps(past_data), content_type="application/json"
        )
        assert response.status_code == 412
        data = response.get_json()
        assert data["msg"] == "Las fechas del trayecto no son válidas"

    @patch("resources.route.SessionLocal")
    def test_create_route_end_before_start(self, mock_session, client):
        """Test de creación con fecha fin antes que fecha inicio"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        invalid_data = {
            "flightId": "FL001",
            "sourceAirportCode": "BOG",
            "sourceCountry": "Colombia",
            "destinyAirportCode": "MDE",
            "destinyCountry": "Colombia",
            "bagCost": 25000,
            "plannedStartDate": "2025-08-25T12:00:00",
            "plannedEndDate": "2025-08-25T10:00:00",
        }
        response = client.post(
            "/routes", data=json.dumps(invalid_data), content_type="application/json"
        )
        assert response.status_code == 412
        data = response.get_json()
        assert data["msg"] == "Las fechas del trayecto no son válidas"

    @patch("resources.route.SessionLocal")
    def test_create_route_duplicate_flight_id(
        self, mock_session, client, sample_route_data
    ):
        """Test de creación con flightId duplicado"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_scalar = MagicMock()
        mock_scalar.scalar_one_or_none.return_value = MagicMock()
        mock_db.execute.return_value = mock_scalar

        response = client.post(
            "/routes",
            data=json.dumps(sample_route_data),
            content_type="application/json",
        )
        assert response.status_code == 412
        assert response.data == b""

    @patch("resources.route.SessionLocal")
    def test_list_routes_empty(self, mock_session, client):
        """Test de listado de rutas vacío"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_db.execute.return_value.scalars.return_value = mock_scalars
        response = client.get("/routes")
        assert response.status_code == 200
        assert response.get_json() == []

    @patch("resources.route.SessionLocal")
    def test_list_routes_with_data(self, mock_session, client, sample_route_model):
        """Test de listado de rutas con datos"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = [sample_route_model]
        mock_db.execute.return_value.scalars.return_value = mock_scalars

        response = client.get("/routes")
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]["id"] == sample_route_model.id
        assert data[0]["flightId"] == sample_route_model.flight_id

    @patch("resources.route.SessionLocal")
    def test_list_routes_with_flight_filter(self, mock_session, client):
        """Test de listado con filtro por flight"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_db.execute.return_value.scalars.return_value = mock_scalars

        response = client.get("/routes?flight=FL001")
        assert response.status_code == 200
        mock_db.execute.assert_called_once()

    def test_list_routes_empty_flight_filter(self, client):
        """Test de listado con filtro flight vacío"""
        response = client.get("/routes?flight=")
        assert response.status_code == 400

    @patch("resources.route.SessionLocal")
    def test_get_route_success(self, mock_session, client, sample_route_model):
        """Test de obtener ruta por ID exitoso"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_db.get.return_value = sample_route_model

        response = client.get(f"/routes/{sample_route_model.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == sample_route_model.id
        assert data["flightId"] == sample_route_model.flight_id

    def test_get_route_invalid_uuid(self, client):
        """Test de obtener ruta con UUID inválido"""
        response = client.get("/routes/invalid-uuid")
        assert response.status_code == 400

    @patch("src.resources.route.SessionLocal")
    def test_get_route_not_found(self, mock_session, client):
        """Test de obtener ruta que no existe"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_db.get.return_value = None
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/routes/{valid_uuid}")
        assert response.status_code == 404

    @patch("resources.route.SessionLocal")
    def test_delete_route_success(self, mock_session, client, sample_route_model):
        """Test de eliminación exitosa de ruta"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_db.get.return_value = sample_route_model

        response = client.delete(f"/routes/{sample_route_model.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["msg"] == "el trayecto fue eliminado"
        mock_db.delete.assert_called_once_with(sample_route_model)
        mock_db.commit.assert_called_once()

    def test_delete_route_invalid_uuid(self, client):
        """Test de eliminación con UUID inválido"""
        response = client.delete("/routes/invalid-uuid")
        assert response.status_code == 400

    @patch("resources.route.SessionLocal")
    def test_delete_route_not_found(self, mock_session, client):
        """Test de eliminación de ruta que no existe"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_db.get.return_value = None
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.delete(f"/routes/{valid_uuid}")
        assert response.status_code == 404

    @patch("resources.route.SessionLocal")
    def test_count_routes(self, mock_session, client):
        """Test de conteo de rutas"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_db.query.return_value.count.return_value = 5

        response = client.get("/routes/count")
        assert response.status_code == 200
        data = response.get_json()
        assert data["count"] == 5

    @patch("src.app.SessionLocal")
    def test_reset_routes(self, mock_session, client):
        """Test de reset de rutas desde /routes/reset"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.delete.return_value = 1

        response = client.post("/routes/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["msg"] == "Todos los datos fueron eliminados"
        # El código del app importa Route desde otro módulo; comparar por nombre
        assert mock_db.query.call_count == 1
        called_arg = mock_db.query.call_args[0][0]
        assert called_arg.__name__ == "Route"
        mock_query.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("src.app.SessionLocal")
    def test_reset_global(self, mock_session, client):
        """Test de reset desde /routes/reset (mismo endpoint que reset_routes)"""
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        mock_query = mock_db.query.return_value
        mock_query.delete.return_value = 1

        response = client.post("/routes/reset")
        assert response.status_code == 200
        data = response.get_json()
        assert data["msg"] == "Todos los datos fueron eliminados"
        # El código del app importa Route desde otro módulo; comparar por nombre
        assert mock_db.query.call_count == 1
        called_arg = mock_db.query.call_args[0][0]
        assert called_arg.__name__ == "Route"
        mock_query.delete.assert_called_once()
        mock_db.commit.assert_called_once()
