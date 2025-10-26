from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, UniqueConstraint

Base = declarative_base()


class Route(Base):
    __tablename__ = "routes"
    id = Column(String(36), primary_key=True)  # uuid string
    flight_id = Column(String(50), nullable=False, unique=True)
    source_airport_code = Column(String(10), nullable=False)
    source_country = Column(String(80), nullable=False)
    destiny_airport_code = Column(String(10), nullable=False)
    destiny_country = Column(String(80), nullable=False)
    bag_cost = Column(Integer, nullable=False)
    planned_start_date = Column(DateTime, nullable=False)  # UTC naive
    planned_end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (UniqueConstraint("flight_id", name="uq_routes_flight_id"),)
