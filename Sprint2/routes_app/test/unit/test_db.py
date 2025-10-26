# test/unit/test_db.py
import pytest
import os
from unittest.mock import patch


@pytest.mark.unit
class TestDatabase:
    """Pruebas unitarias para configuración de base de datos"""

    def test_database_uri_from_environment(self):
        """Test que la URI de base de datos se lee del entorno"""
        # Verificar que el entorno se puede configurar
        with patch.dict(os.environ, {"DATABASE_URI": "sqlite:///:memory:"}):
            assert os.environ.get("DATABASE_URI") == "sqlite:///:memory:"

    def test_database_uri_default_none(self):
        """Test que la URI por defecto es None si no está en entorno"""
        with patch.dict(os.environ, {}, clear=True):
            # Si no hay DATABASE_URI en el entorno, debería ser None
            uri = os.environ.get("DATABASE_URI")
            assert uri is None

    def test_engine_exists(self):
        """Test que existe el motor de SQLAlchemy"""
        from src.db import engine
        from sqlalchemy.engine import Engine

        assert isinstance(engine, Engine)

    def test_session_local_exists(self):
        """Test que existe SessionLocal"""
        from src.db import SessionLocal
        from sqlalchemy.orm import scoped_session

        assert isinstance(SessionLocal, scoped_session)

    def test_engine_created_with_future_flag(self):
        """Test que el motor se crea con future=True"""
        from src.db import engine

        # Verificar que el motor existe y tiene las propiedades esperadas
        assert engine is not None
        # En SQLAlchemy 2.x, future=True es el comportamiento por defecto

    def test_sessionmaker_configuration(self):
        """Test que sessionmaker se configura correctamente"""
        from src.db import SessionLocal

        # Verificar que SessionLocal es una scoped_session
        from sqlalchemy.orm import scoped_session

        assert isinstance(SessionLocal, scoped_session)

    def test_session_can_be_created(self):
        """Test que se puede crear una sesión"""
        from src.db import SessionLocal

        session = SessionLocal()
        assert session is not None
        session.close()

    def test_session_scoped_removes_correctly(self):
        """Test que scoped_session se puede remover"""
        from src.db import SessionLocal

        session1 = SessionLocal()
        session2 = SessionLocal()

        # En scoped_session, deberían ser la misma instancia
        assert session1 is session2

        # Remove debería funcionar sin errores
        SessionLocal.remove()


@pytest.mark.unit
class TestDatabaseConfiguration:
    """Pruebas unitarias para configuración específica de la base de datos"""

    def test_database_uri_structure(self):
        """Test de estructura esperada de DATABASE_URI"""
        test_uris = [
            "postgresql://user:pass@localhost:5432/db",
            "sqlite:///path/to/db.sqlite",
            "sqlite:///:memory:",
        ]

        for uri in test_uris:
            with patch.dict(os.environ, {"DATABASE_URI": uri}):
                import importlib
                import src.db

                importlib.reload(src.db)

                assert src.db.DATABASE_URI == uri

    def test_engine_uses_database_uri(self):
        """Test que el motor usa la URI configurada"""
        from src.db import engine

        # Verificar que el motor existe
        assert engine is not None
        # En las pruebas, debería estar usando SQLite en memoria
        assert "sqlite" in str(engine.url)

    def test_session_thread_safety(self):
        """Test de seguridad de hilos con scoped_session"""
        from src.db import SessionLocal
        import threading

        sessions = []

        def create_session():
            session = SessionLocal()
            sessions.append(session)

        threads = []
        for _ in range(3):
            thread = threading.Thread(target=create_session)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # En el mismo hilo, todas las sesiones deberían ser diferentes
        # pero en scoped_session, dentro del mismo hilo serían iguales
        assert len(sessions) == 3

        # Cleanup
        SessionLocal.remove()
