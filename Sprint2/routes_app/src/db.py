import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URI = os.getenv("DATABASE_URI")

# SQLAlchemy 2.x
engine = create_engine(DATABASE_URI, future=True)

# scoped_session para seguridad en hilos
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
)
