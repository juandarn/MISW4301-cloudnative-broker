# test/conftest.py
import pytest
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database de pruebas en memoria
TEST_DATABASE_URL = "sqlite:///:memory:"
os.environ["DATABASE_URI"] = TEST_DATABASE_URL

from src.app import create_app
from src.models.route import Base, Route


@pytest.fixture(scope="session")
def test_engine():
    """Motor de base de datos para pruebas"""
    engine = create_engine(TEST_DATABASE_URL, future=True)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Sesión de base de datos para cada test"""
    TestSessionLocal = sessionmaker(bind=test_engine, future=True)
    session = TestSessionLocal()

    # Limpiar tablas antes de cada test
    session.query(Route).delete()
    session.commit()

    yield session

    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def app(test_db_session):
    """Aplicación Flask configurada para pruebas"""
    # Configurar para usar la sesión de prueba
    app = create_app()
    app.config["TESTING"] = True
    app.config["DATABASE_URL"] = TEST_DATABASE_URL

    # Para pruebas, usamos un mock más simple
    with app.test_request_context():
        yield app


@pytest.fixture(scope="function")
def client(app):
    """Cliente de prueba Flask"""
    return app.test_client()


@pytest.fixture
def sample_route_data():
    """Datos de ejemplo para crear una ruta"""
    now = datetime.utcnow()
    start_date = (now + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    end_date = (now + timedelta(days=1, hours=2)).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "flightId": "FL001",
        "sourceAirportCode": "BOG",
        "sourceCountry": "Colombia",
        "destinyAirportCode": "MDE",
        "destinyCountry": "Colombia",
        "bagCost": 25000,
        "plannedStartDate": start_date,
        "plannedEndDate": end_date,
    }


@pytest.fixture
def sample_route_model(test_db_session):
    """Modelo de ruta de ejemplo en la base de datos"""
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
    test_db_session.add(route)
    test_db_session.commit()
    return route


def utc_now_naive():
    """Utility para obtener fecha UTC naive para pruebas"""
    return datetime.now(timezone.utc).replace(tzinfo=None)
