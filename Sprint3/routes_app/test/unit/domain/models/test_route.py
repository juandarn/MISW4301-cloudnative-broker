# test/unit/domain/models/test_route.py
import pytest
from datetime import datetime
from src.models.route import Route


@pytest.mark.unit
class TestRouteModel:
    """Pruebas unitarias para el modelo Route"""

    def test_route_creation(self):
        """Test de creación de instancia Route"""
        route = Route(
            id="123e4567-e89b-12d3-a456-426614174000",
            flight_id="FL001",
            source_airport_code="BOG",
            source_country="Colombia",
            destiny_airport_code="MDE",
            destiny_country="Colombia",
            bag_cost=25000,
            planned_start_date=datetime(2025, 8, 25, 10, 0, 0),
            planned_end_date=datetime(2025, 8, 25, 12, 0, 0),
            created_at=datetime(2025, 8, 22, 8, 0, 0),
            updated_at=datetime(2025, 8, 22, 8, 0, 0),
        )

        assert route.id == "123e4567-e89b-12d3-a456-426614174000"
        assert route.flight_id == "FL001"
        assert route.source_airport_code == "BOG"
        assert route.source_country == "Colombia"
        assert route.destiny_airport_code == "MDE"
        assert route.destiny_country == "Colombia"
        assert route.bag_cost == 25000
        assert route.planned_start_date == datetime(2025, 8, 25, 10, 0, 0)
        assert route.planned_end_date == datetime(2025, 8, 25, 12, 0, 0)
        assert route.created_at == datetime(2025, 8, 22, 8, 0, 0)
        assert route.updated_at == datetime(2025, 8, 22, 8, 0, 0)

    def test_route_tablename(self):
        """Test del nombre de tabla"""
        assert Route.__tablename__ == "routes"

    def test_route_primary_key(self):
        """Test de clave primaria"""
        route = Route()
        assert hasattr(route, "id")
        assert Route.id.primary_key is True

    def test_route_unique_constraint_flight_id(self):
        """Test de restricción única en flight_id"""
        # Verificar que existe la restricción única
        constraint_names = [
            constraint.name for constraint in Route.__table__.constraints
        ]
        assert "uq_routes_flight_id" in constraint_names

        # Verificar que la restricción es sobre flight_id
        unique_constraint = next(
            constraint
            for constraint in Route.__table__.constraints
            if constraint.name == "uq_routes_flight_id"
        )
        assert "flight_id" in [col.name for col in unique_constraint.columns]

    def test_route_columns_not_nullable(self):
        """Test de columnas que no pueden ser nulas"""
        assert Route.flight_id.nullable is False
        assert Route.source_airport_code.nullable is False
        assert Route.source_country.nullable is False
        assert Route.destiny_airport_code.nullable is False
        assert Route.destiny_country.nullable is False
        assert Route.bag_cost.nullable is False
        assert Route.planned_start_date.nullable is False
        assert Route.planned_end_date.nullable is False
        assert Route.created_at.nullable is False
        assert Route.updated_at.nullable is False

    def test_route_column_types(self):
        """Test de tipos de columnas"""
        from sqlalchemy import String, Integer, DateTime

        assert isinstance(Route.id.type, String)
        assert isinstance(Route.flight_id.type, String)
        assert isinstance(Route.source_airport_code.type, String)
        assert isinstance(Route.source_country.type, String)
        assert isinstance(Route.destiny_airport_code.type, String)
        assert isinstance(Route.destiny_country.type, String)
        assert isinstance(Route.bag_cost.type, Integer)
        assert isinstance(Route.planned_start_date.type, DateTime)
        assert isinstance(Route.planned_end_date.type, DateTime)
        assert isinstance(Route.created_at.type, DateTime)
        assert isinstance(Route.updated_at.type, DateTime)

    def test_route_string_lengths(self):
        """Test de longitudes de campos string"""
        assert Route.id.type.length == 36  # UUID length
        assert Route.flight_id.type.length == 50
        assert Route.source_airport_code.type.length == 10
        assert Route.source_country.type.length == 80
        assert Route.destiny_airport_code.type.length == 10
        assert Route.destiny_country.type.length == 80
