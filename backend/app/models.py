"""
Modelos do banco de dados (SQLAlchemy ORM)
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base


class AlertType(str, enum.Enum):
    """Tipos de alerta de fadiga"""
    EYES_CLOSED = "eyes_closed"
    YAWNING = "yawning"


class AlertSeverity(str, enum.Enum):
    """Severidade do alerta"""
    MODERATE = "moderate"
    CRITICAL = "critical"


class Vehicle(Base):
    """Modelo de veículo"""
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(200), nullable=False)
    placa = Column(String(20), nullable=False, unique=True, index=True)
    motorista = Column(String(200), nullable=True)
    frota = Column(String(100), nullable=True)
    rota = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento com alertas
    alerts = relationship("Alert", back_populates="vehicle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vehicle(placa='{self.placa}', nome='{self.nome}')>"


class Alert(Base):
    """Modelo de alerta de fadiga"""
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    tipo = Column(SQLEnum(AlertType), nullable=False, index=True)
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    ear_value = Column(Float, nullable=False)
    mar_value = Column(Float, nullable=False)
    image_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamento com veículo
    vehicle = relationship("Vehicle", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(tipo='{self.tipo}', severity='{self.severity}', timestamp='{self.timestamp}')>"

