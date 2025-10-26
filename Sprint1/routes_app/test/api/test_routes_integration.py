# test/api/test_routes_integration.py
import pytest
import json
from datetime import datetime, timedelta


@pytest.mark.api
class TestRoutesIntegration:
    """Pruebas de integración para la API de rutas"""

    def test_full_route_lifecycle(self, client):
        """Test del ciclo completo de una ruta: crear, consultar, eliminar"""
        # 1. Crear una ruta
        future_date = datetime.now() + timedelta(days=1)
        route_data = {
            "flightId": "FL001-INTEGRATION",
            "sourceAirportCode": "BOG",
            "sourceCountry": "Colombia",
            "destinyAirportCode": "MDE",
            "destinyCountry": "Colombia",
            "bagCost": 25000,
            "plannedStartDate": future_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "plannedEndDate": (future_date + timedelta(hours=2)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
        }

        create_response = client.post(
            "/routes", data=json.dumps(route_data), content_type="application/json"
        )

        assert create_response.status_code == 201
        create_data = create_response.get_json()
        route_id = create_data["id"]
        assert "createdAt" in create_data

        # 2. Consultar la ruta creada
        get_response = client.get(f"/routes/{route_id}")
        assert get_response.status_code == 200

        get_data = get_response.get_json()
        assert get_data["id"] == route_id
        assert get_data["flightId"] == route_data["flightId"]
        assert get_data["sourceAirportCode"] == route_data["sourceAirportCode"]
        assert get_data["bagCost"] == route_data["bagCost"]

        # 3. Verificar que aparece en la lista
        list_response = client.get("/routes")
        assert list_response.status_code == 200

        list_data = list_response.get_json()
        route_ids = [route["id"] for route in list_data]
        assert route_id in route_ids

        # 4. Filtrar por flightId
        filter_response = client.get(f"/routes?flight={route_data['flightId']}")
        assert filter_response.status_code == 200

        filter_data = filter_response.get_json()
        assert len(filter_data) == 1
        assert filter_data[0]["id"] == route_id

        # 5. Verificar contador
        count_response = client.get("/routes/count")
        assert count_response.status_code == 200

        count_data = count_response.get_json()
        assert count_data["count"] >= 1

        # 6. Eliminar la ruta
        delete_response = client.delete(f"/routes/{route_id}")
        assert delete_response.status_code == 200

        delete_data = delete_response.get_json()
        assert delete_data["msg"] == "el trayecto fue eliminado"

        # 7. Verificar que ya no existe
        get_deleted_response = client.get(f"/routes/{route_id}")
        assert get_deleted_response.status_code == 404

    def test_duplicate_flight_id_prevention(self, client):
        """Test de prevención de flightId duplicado"""
        future_date = datetime.now() + timedelta(days=1)
        route_data = {
            "flightId": "FL002-DUPLICATE",
            "sourceAirportCode": "BOG",
            "sourceCountry": "Colombia",
            "destinyAirportCode": "MDE",
            "destinyCountry": "Colombia",
            "bagCost": 25000,
            "plannedStartDate": future_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "plannedEndDate": (future_date + timedelta(hours=2)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
        }

        # Crear primera ruta
        first_response = client.post(
            "/routes", data=json.dumps(route_data), content_type="application/json"
        )
        assert first_response.status_code == 201

        # Intentar crear segunda ruta con mismo flightId
        second_response = client.post(
            "/routes", data=json.dumps(route_data), content_type="application/json"
        )
        assert second_response.status_code == 412
        assert second_response.data == b""  # Sin cuerpo

        # Limpiar
        first_data = first_response.get_json()
        client.delete(f"/routes/{first_data['id']}")

    def test_date_validation_scenarios(self, client):
        """Test de diferentes escenarios de validación de fechas"""
        base_data = {
            "flightId": "FL003-DATES",
            "sourceAirportCode": "BOG",
            "sourceCountry": "Colombia",
            "destinyAirportCode": "MDE",
            "destinyCountry": "Colombia",
            "bagCost": 25000,
        }

        # Escenario 1: Fecha de inicio en el pasado
        past_data = base_data.copy()
        past_data.update(
            {
                "plannedStartDate": "2020-01-01T10:00:00",
                "plannedEndDate": "2020-01-01T12:00:00",
            }
        )

        response = client.post(
            "/routes", data=json.dumps(past_data), content_type="application/json"
        )
        assert response.status_code == 412
        assert response.get_json()["msg"] == "Las fechas del trayecto no son válidas"

        # Escenario 2: Fecha fin antes que fecha inicio
        future_date = datetime.now() + timedelta(days=1)
        invalid_order_data = base_data.copy()
        invalid_order_data.update(
            {
                "plannedStartDate": future_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "plannedEndDate": (future_date - timedelta(hours=1)).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
            }
        )

        response = client.post(
            "/routes",
            data=json.dumps(invalid_order_data),
            content_type="application/json",
        )
        assert response.status_code == 412
        assert response.get_json()["msg"] == "Las fechas del trayecto no son válidas"

        # Escenario 3: Formato de fecha inválido
        invalid_format_data = base_data.copy()
        invalid_format_data.update(
            {
                "plannedStartDate": "invalid-date-format",
                "plannedEndDate": future_date.strftime("%Y-%m-%dT%H:%M:%S"),
            }
        )

        response = client.post(
            "/routes",
            data=json.dumps(invalid_format_data),
            content_type="application/json",
        )
        assert response.status_code == 412
        assert response.get_json()["msg"] == "Las fechas del trayecto no son válidas"

    def test_filtering_and_search(self, client):
        """Test de filtrado y búsqueda"""
        future_date = datetime.now() + timedelta(days=1)

        # Crear múltiples rutas
        routes_data = [
            {
                "flightId": "FL004-FILTER-1",
                "sourceAirportCode": "BOG",
                "sourceCountry": "Colombia",
                "destinyAirportCode": "MDE",
                "destinyCountry": "Colombia",
                "bagCost": 25000,
                "plannedStartDate": future_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "plannedEndDate": (future_date + timedelta(hours=2)).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
            },
            {
                "flightId": "FL005-FILTER-2",
                "sourceAirportCode": "MDE",
                "sourceCountry": "Colombia",
                "destinyAirportCode": "CTG",
                "destinyCountry": "Colombia",
                "bagCost": 30000,
                "plannedStartDate": (future_date + timedelta(hours=3)).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
                "plannedEndDate": (future_date + timedelta(hours=5)).strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),
            },
        ]

        created_routes = []
        for route_data in routes_data:
            response = client.post(
                "/routes", data=json.dumps(route_data), content_type="application/json"
            )
            assert response.status_code == 201
            created_routes.append(response.get_json())

        # Test filtro por flight específico
        filter_response = client.get(f"/routes?flight={routes_data[0]['flightId']}")
        assert filter_response.status_code == 200

        filter_data = filter_response.get_json()
        assert len(filter_data) == 1
        assert filter_data[0]["flightId"] == routes_data[0]["flightId"]

        # Test listado sin filtros (debe incluir ambas)
        all_response = client.get("/routes")
        assert all_response.status_code == 200

        all_data = all_response.get_json()
        flight_ids = [route["flightId"] for route in all_data]
        assert routes_data[0]["flightId"] in flight_ids
        assert routes_data[1]["flightId"] in flight_ids

        # Limpiar rutas creadas
        for created_route in created_routes:
            client.delete(f"/routes/{created_route['id']}")

    def test_error_handling(self, client):
        """Test de manejo de errores"""
        # Test 400: JSON malformado
        response = client.post(
            "/routes", data="invalid-json", content_type="application/json"
        )
        assert response.status_code == 400

        # Test 400: Campos faltantes
        incomplete_data = {"flightId": "FL006-INCOMPLETE"}
        response = client.post(
            "/routes", data=json.dumps(incomplete_data), content_type="application/json"
        )
        assert response.status_code == 400

        # Test 400: UUID inválido en GET
        response = client.get("/routes/invalid-uuid")
        assert response.status_code == 400

        # Test 400: UUID inválido en DELETE
        response = client.delete("/routes/invalid-uuid")
        assert response.status_code == 400

        # Test 404: Ruta no existe
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = client.get(f"/routes/{valid_uuid}")
        assert response.status_code == 404

        response = client.delete(f"/routes/{valid_uuid}")
        assert response.status_code == 404

        # Test 400: Filtro flight vacío
        response = client.get("/routes?flight=")
        assert response.status_code == 400

    def test_ping_endpoints(self, client):
        """Test de endpoints de ping"""
        # Test ping de rutas
        response = client.get("/routes/ping")
        assert response.status_code == 200
        assert response.data == b"pong"
        assert response.content_type == "text/plain; charset=utf-8"

    def test_reset_functionality(self, client):
        """Test de funcionalidad de reset"""
        # Crear una ruta de prueba
        future_date = datetime.now() + timedelta(days=1)
        route_data = {
            "flightId": "FL007-RESET",
            "sourceAirportCode": "BOG",
            "sourceCountry": "Colombia",
            "destinyAirportCode": "MDE",
            "destinyCountry": "Colombia",
            "bagCost": 25000,
            "plannedStartDate": future_date.strftime("%Y-%m-%dT%H:%M:%S"),
            "plannedEndDate": (future_date + timedelta(hours=2)).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
        }

        create_response = client.post(
            "/routes", data=json.dumps(route_data), content_type="application/json"
        )
        assert create_response.status_code == 201

        # Verificar que existe
        list_response = client.get("/routes")
        assert list_response.status_code == 200
        initial_count = len(list_response.get_json())
        assert initial_count > 0

        # Reset desde /routes/reset
        reset_response = client.post("/routes/reset")
        assert reset_response.status_code == 200
        assert reset_response.get_json()["msg"] == "Todos los datos fueron eliminados"

        # Verificar que se eliminaron
        list_response = client.get("/routes")
        assert list_response.status_code == 200
        assert len(list_response.get_json()) == 0

        # Crear otra ruta para probar reset desde /routes/reset otra vez
        create_response = client.post(
            "/routes", data=json.dumps(route_data), content_type="application/json"
        )
        assert create_response.status_code == 201

        # Reset desde /routes/reset nuevamente
        reset_response = client.post("/routes/reset")
        assert reset_response.status_code == 200
        assert reset_response.get_json()["msg"] == "Todos los datos fueron eliminados"

        # Verificar que se eliminaron
        list_response = client.get("/routes")
        assert list_response.status_code == 200
        assert len(list_response.get_json()) == 0
