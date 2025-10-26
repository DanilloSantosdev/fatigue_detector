"""
Schemas Pydantic para validação e serialização
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from .models import AlertType, AlertSeverity


# ============================================================================
# VEHICLE SCHEMAS
# ============================================================================

class VehicleBase(BaseModel):
    """Schema base para veículo"""
    nome: str = Field(..., min_length=1, max_length=200, description="Nome/descrição do veículo")
    placa: str = Field(..., min_length=1, max_length=20, description="Placa do veículo")
    motorista: Optional[str] = Field(None, max_length=200, description="Nome do motorista")
    frota: Optional[str] = Field(None, max_length=100, description="Identificação da frota")
    rota: Optional[str] = Field(None, max_length=200, description="Rota/linha do veículo")


class VehicleCreate(VehicleBase):
    """Schema para criação de veículo"""
    pass


class VehicleUpdate(BaseModel):
    """Schema para atualização de veículo"""
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    placa: Optional[str] = Field(None, min_length=1, max_length=20)
    motorista: Optional[str] = Field(None, max_length=200)
    frota: Optional[str] = Field(None, max_length=100)
    rota: Optional[str] = Field(None, max_length=200)


class VehicleResponse(VehicleBase):
    """Schema de resposta de veículo"""
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# ALERT SCHEMAS
# ============================================================================

class AlertBase(BaseModel):
    """Schema base para alerta"""
    vehicle_id: UUID = Field(..., description="ID do veículo")
    timestamp: datetime = Field(..., description="Data e hora do alerta")
    tipo: AlertType = Field(..., description="Tipo de alerta")
    severity: AlertSeverity = Field(..., description="Severidade do alerta")
    ear_value: float = Field(..., ge=0, le=1, description="Eye Aspect Ratio")
    mar_value: float = Field(..., ge=0, description="Mouth Aspect Ratio")


class AlertCreate(AlertBase):
    """Schema para criação de alerta (usado pelo detector)"""
    image_filename: Optional[str] = Field(None, description="Nome do arquivo de imagem")


class AlertResponse(AlertBase):
    """Schema de resposta de alerta"""
    id: UUID
    image_path: Optional[str]
    created_at: datetime
    vehicle: Optional[VehicleResponse] = None

    model_config = ConfigDict(from_attributes=True)


class AlertListResponse(BaseModel):
    """Schema para lista de alertas com paginação"""
    total: int
    page: int
    page_size: int
    items: list[AlertResponse]


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================

class AlertStats(BaseModel):
    """Estatísticas de alertas"""
    total_alerts: int
    eyes_closed_count: int
    yawning_count: int
    critical_count: int
    moderate_count: int
    alerts_by_vehicle: dict[str, int]
    recent_alerts: list[AlertResponse]


# ============================================================================
# REPORT SCHEMAS
# ============================================================================

class ReportRequest(BaseModel):
    """Schema para requisição de relatório"""
    format: str = Field(..., pattern="^(pdf|excel)$", description="Formato: pdf ou excel")
    date_from: Optional[datetime] = Field(None, description="Data inicial")
    date_to: Optional[datetime] = Field(None, description="Data final")
    vehicle_id: Optional[UUID] = Field(None, description="ID do veículo (opcional)")
    include_images: bool = Field(default=False, description="Incluir imagens no relatório")

