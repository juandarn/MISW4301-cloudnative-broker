# test/unit/schemas/test_schemas.py
import pytest
from datetime import datetime, timezone
from marshmallow import ValidationError
from src.schemas import (
    RouteCreateSchema,
    RouteOutSchema,
    to_iso_utc,
    utc_now_naive,
    parse_iso_naive,
    is_valid_uuid,
)


@pytest.mark.unit
class TestSchemaUtilities:
    """Pruebas unitarias para utilidades de schemas"""

    def test_to_iso_utc_naive_datetime(self):
        """Test de conversión de datetime naive a ISO UTC"""
        dt = datetime(2025, 8, 25, 10, 30, 45)
        result = to_iso_utc(dt)
        assert result == "2025-08-25T10:30:45"

    def test_to_iso_utc_aware_datetime(self):
        """Test de conversión de datetime con timezone a ISO UTC"""
        dt = datetime(2025, 8, 25, 10, 30, 45, tzinfo=timezone.utc)
        result = to_iso_utc(dt)
        assert result == "2025-08-25T10:30:45"

    def test_utc_now_naive(self):
        """Test de obtener fecha UTC naive actual"""
        result = utc_now_naive()
        assert isinstance(result, datetime)
        assert result.tzinfo is None
        # Verificar que es aproximadamente ahora (dentro de 1 segundo)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        assert abs((result - now).total_seconds()) < 1

    def test_parse_iso_naive_basic_format(self):
        """Test de parsing de ISO básico"""
        iso_string = "2025-08-25T10:30:45"
        result = parse_iso_naive(iso_string)
        expected = datetime(2025, 8, 25, 10, 30, 45)
        assert result == expected
        assert result.tzinfo is None

    def test_parse_iso_naive_with_z_suffix(self):
        """Test de parsing de ISO con sufijo Z"""
        iso_string = "2025-08-25T10:30:45Z"
        result = parse_iso_naive(iso_string)
        expected = datetime(2025, 8, 25, 10, 30, 45)
        assert result == expected
        assert result.tzinfo is None

    def test_parse_iso_naive_with_offset(self):
        """Test de parsing de ISO con offset de timezone"""
        iso_string = "2025-08-25T10:30:45+05:00"
        result = parse_iso_naive(iso_string)
        # Debería convertir a UTC y quitar timezone info
        expected = datetime(2025, 8, 25, 5, 30, 45)  # 10:30 - 5 horas = 5:30 UTC
        assert result == expected
        assert result.tzinfo is None

    def test_parse_iso_naive_invalid_format(self):
        """Test de parsing con formato inválido"""
        with pytest.raises(ValidationError):
            parse_iso_naive("invalid-date-format")

    def test_is_valid_uuid_valid(self):
        """Test de validación de UUID válido"""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        assert is_valid_uuid(valid_uuid) is True

    def test_is_valid_uuid_invalid(self):
        """Test de validación de UUID inválido"""
        invalid_uuid = "not-a-uuid"
        assert is_valid_uuid(invalid_uuid) is False

    def test_is_valid_uuid_empty(self):
        """Test de validación de UUID vacío"""
        assert is_valid_uuid("") is False

    def test_is_valid_uuid_none(self):
        """Test de validación de UUID None"""
        assert is_valid_uuid(None) is False


@pytest.mark.unit
class TestRouteCreateSchema:
    """Pruebas unitarias para RouteCreateSchema"""

    def test_valid_route_data(self, sample_route_data):
        """Test de validación de datos válidos"""
        schema = RouteCreateSchema()
        result = schema.load(sample_route_data)
        assert result == sample_route_data

    def test_missing_required_fields(self):
        """Test de validación con campos requeridos faltantes"""
        schema = RouteCreateSchema()
        incomplete_data = {
            "flightId": "FL001",
            "sourceAirportCode": "BOG",
            # Faltan campos requeridos
        }

        errors = schema.validate(incomplete_data)
        required_fields = [
            "sourceCountry",
            "destinyAirportCode",
            "destinyCountry",
            "bagCost",
            "plannedStartDate",
            "plannedEndDate",
        ]

        for field in required_fields:
            assert field in errors

    def test_empty_data(self):
        """Test de validación con datos vacíos"""
        schema = RouteCreateSchema()
        errors = schema.validate({})

        required_fields = [
            "flightId",
            "sourceAirportCode",
            "sourceCountry",
            "destinyAirportCode",
            "destinyCountry",
            "bagCost",
            "plannedStartDate",
            "plannedEndDate",
        ]

        for field in required_fields:
            assert field in errors

    def test_invalid_bag_cost_type(self):
        """Test de validación con tipo incorrecto para bagCost"""
        schema = RouteCreateSchema()
        invalid_data = {
            "flightId": "FL001",
            "sourceAirportCode": "BOG",
            "sourceCountry": "Colombia",
            "destinyAirportCode": "MDE",
            "destinyCountry": "Colombia",
            "bagCost": "not-a-number",  # Tipo incorrecto
            "plannedStartDate": "2025-08-25T10:00:00",
            "plannedEndDate": "2025-08-25T12:00:00",
        }

        errors = schema.validate(invalid_data)
        assert "bagCost" in errors


@pytest.mark.unit
class TestRouteOutSchema:
    """Pruebas unitarias para RouteOutSchema"""

    def test_valid_route_output_single(self):
        """Test de serialización de ruta única"""
        schema = RouteOutSchema()
        route_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "flightId": "FL001",
            "sourceAirportCode": "BOG",
            "sourceCountry": "Colombia",
            "destinyAirportCode": "MDE",
            "destinyCountry": "Colombia",
            "bagCost": 25000,
            "plannedStartDate": "2025-08-25T10:00:00",
            "plannedEndDate": "2025-08-25T12:00:00",
            "createdAt": "2025-08-22T08:00:00",
        }

        result = schema.dump(route_data)
        assert result == route_data

    def test_valid_route_output_multiple(self):
        """Test de serialización de múltiples rutas"""
        schema = RouteOutSchema(many=True)
        routes_data = [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "flightId": "FL001",
                "sourceAirportCode": "BOG",
                "sourceCountry": "Colombia",
                "destinyAirportCode": "MDE",
                "destinyCountry": "Colombia",
                "bagCost": 25000,
                "plannedStartDate": "2025-08-25T10:00:00",
                "plannedEndDate": "2025-08-25T12:00:00",
                "createdAt": "2025-08-22T08:00:00",
            },
            {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "flightId": "FL002",
                "sourceAirportCode": "MDE",
                "sourceCountry": "Colombia",
                "destinyAirportCode": "BOG",
                "destinyCountry": "Colombia",
                "bagCost": 30000,
                "plannedStartDate": "2025-08-26T14:00:00",
                "plannedEndDate": "2025-08-26T16:00:00",
                "createdAt": "2025-08-22T09:00:00",
            },
        ]

        result = schema.dump(routes_data)
        assert result == routes_data
        assert len(result) == 2

    def test_missing_required_output_fields(self):
        """Test de validación de campos requeridos en output"""
        schema = RouteOutSchema()
        incomplete_data = {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "flightId": "FL001",
            # Faltan campos requeridos
        }

        errors = schema.validate(incomplete_data)
        required_fields = [
            "sourceAirportCode",
            "sourceCountry",
            "destinyAirportCode",
            "destinyCountry",
            "bagCost",
            "plannedStartDate",
            "plannedEndDate",
            "createdAt",
        ]

        for field in required_fields:
            assert field in errors
