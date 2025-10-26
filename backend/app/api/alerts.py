"""
Endpoints para gerenciamento de alertas de fadiga
"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas import AlertCreate, AlertResponse, AlertListResponse, AlertStats
from ..models import AlertType, AlertSeverity
from .. import crud

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert: AlertCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Cria um novo alerta (usado pelo detector de fadiga)
    """
    # Verificar se veículo existe
    vehicle = await crud.get_vehicle(db, alert.vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Veículo com ID '{alert.vehicle_id}' não encontrado"
        )
    
    db_alert = await crud.create_alert(db, alert)
    return db_alert


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(50, ge=1, le=100, description="Items por página"),
    vehicle_id: Optional[UUID] = Query(None, description="Filtrar por veículo"),
    tipo: Optional[AlertType] = Query(None, description="Filtrar por tipo"),
    severity: Optional[AlertSeverity] = Query(None, description="Filtrar por severidade"),
    date_from: Optional[datetime] = Query(None, description="Data inicial"),
    date_to: Optional[datetime] = Query(None, description="Data final"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista alertas com filtros e paginação
    """
    skip = (page - 1) * page_size
    
    alerts, total = await crud.get_alerts(
        db,
        skip=skip,
        limit=page_size,
        vehicle_id=vehicle_id,
        tipo=tipo,
        severity=severity,
        date_from=date_from,
        date_to=date_to
    )
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": alerts
    }


@router.get("/stats", response_model=AlertStats)
async def get_alert_statistics(
    date_from: Optional[datetime] = Query(None, description="Data inicial"),
    date_to: Optional[datetime] = Query(None, description="Data final"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna estatísticas dos alertas
    """
    stats = await crud.get_alert_stats(db, date_from=date_from, date_to=date_to)
    return stats


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Busca um alerta específico por ID
    """
    alert = await crud.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta não encontrado"
        )
    return alert

