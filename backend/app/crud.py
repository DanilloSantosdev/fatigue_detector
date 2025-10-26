"""
Operações CRUD (Create, Read, Update, Delete) para o banco de dados
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import Vehicle, Alert, AlertType, AlertSeverity
from .schemas import VehicleCreate, VehicleUpdate, AlertCreate


# ============================================================================
# VEHICLE CRUD
# ============================================================================

async def create_vehicle(db: AsyncSession, vehicle: VehicleCreate) -> Vehicle:
    """Cria um novo veículo"""
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle


async def get_vehicle(db: AsyncSession, vehicle_id: UUID) -> Optional[Vehicle]:
    """Busca um veículo por ID"""
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    return result.scalar_one_or_none()


async def get_vehicle_by_placa(db: AsyncSession, placa: str) -> Optional[Vehicle]:
    """Busca um veículo pela placa"""
    result = await db.execute(select(Vehicle).where(Vehicle.placa == placa))
    return result.scalar_one_or_none()


async def get_vehicles(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Vehicle]:
    """Lista todos os veículos com paginação"""
    result = await db.execute(
        select(Vehicle)
        .order_by(desc(Vehicle.created_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_vehicle(
    db: AsyncSession,
    vehicle_id: UUID,
    vehicle_update: VehicleUpdate
) -> Optional[Vehicle]:
    """Atualiza um veículo"""
    db_vehicle = await get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return None
    
    update_data = vehicle_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    
    await db.commit()
    await db.refresh(db_vehicle)
    return db_vehicle


async def delete_vehicle(db: AsyncSession, vehicle_id: UUID) -> bool:
    """Deleta um veículo"""
    db_vehicle = await get_vehicle(db, vehicle_id)
    if not db_vehicle:
        return False
    
    await db.delete(db_vehicle)
    await db.commit()
    return True


# ============================================================================
# ALERT CRUD
# ============================================================================

async def create_alert(db: AsyncSession, alert: AlertCreate) -> Alert:
    """Cria um novo alerta"""
    alert_data = alert.model_dump(exclude={"image_filename"})
    
    # Adicionar caminho da imagem se fornecido
    if alert.image_filename:
        alert_data["image_path"] = f"/uploads/{alert.image_filename}"
    
    db_alert = Alert(**alert_data)
    db.add(db_alert)
    await db.commit()
    await db.refresh(db_alert)
    
    # Carregar relacionamento com veículo
    await db.refresh(db_alert, attribute_names=["vehicle"])
    
    return db_alert


async def get_alert(db: AsyncSession, alert_id: UUID) -> Optional[Alert]:
    """Busca um alerta por ID (com dados do veículo)"""
    result = await db.execute(
        select(Alert)
        .options(selectinload(Alert.vehicle))
        .where(Alert.id == alert_id)
    )
    return result.scalar_one_or_none()


async def get_alerts(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    vehicle_id: Optional[UUID] = None,
    tipo: Optional[AlertType] = None,
    severity: Optional[AlertSeverity] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> tuple[List[Alert], int]:
    """
    Lista alertas com filtros e paginação
    Retorna (lista_de_alertas, total_count)
    """
    # Construir query base
    conditions = []
    
    if vehicle_id:
        conditions.append(Alert.vehicle_id == vehicle_id)
    if tipo:
        conditions.append(Alert.tipo == tipo)
    if severity:
        conditions.append(Alert.severity == severity)
    if date_from:
        conditions.append(Alert.timestamp >= date_from)
    if date_to:
        conditions.append(Alert.timestamp <= date_to)
    
    where_clause = and_(*conditions) if conditions else True
    
    # Query para dados
    query = (
        select(Alert)
        .options(selectinload(Alert.vehicle))
        .where(where_clause)
        .order_by(desc(Alert.timestamp))
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    # Query para count total
    count_query = select(func.count()).select_from(Alert).where(where_clause)
    count_result = await db.execute(count_query)
    total = count_result.scalar()
    
    return alerts, total


async def get_alert_stats(
    db: AsyncSession,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> dict:
    """Retorna estatísticas dos alertas"""
    # Filtros de data
    conditions = []
    if date_from:
        conditions.append(Alert.timestamp >= date_from)
    if date_to:
        conditions.append(Alert.timestamp <= date_to)
    
    where_clause = and_(*conditions) if conditions else True
    
    # Total de alertas
    total_result = await db.execute(
        select(func.count()).select_from(Alert).where(where_clause)
    )
    total_alerts = total_result.scalar()
    
    # Contagem por tipo
    eyes_closed_result = await db.execute(
        select(func.count())
        .select_from(Alert)
        .where(and_(where_clause, Alert.tipo == AlertType.EYES_CLOSED))
    )
    eyes_closed_count = eyes_closed_result.scalar()
    
    yawning_result = await db.execute(
        select(func.count())
        .select_from(Alert)
        .where(and_(where_clause, Alert.tipo == AlertType.YAWNING))
    )
    yawning_count = yawning_result.scalar()
    
    # Contagem por severidade
    critical_result = await db.execute(
        select(func.count())
        .select_from(Alert)
        .where(and_(where_clause, Alert.severity == AlertSeverity.CRITICAL))
    )
    critical_count = critical_result.scalar()
    
    moderate_result = await db.execute(
        select(func.count())
        .select_from(Alert)
        .where(and_(where_clause, Alert.severity == AlertSeverity.MODERATE))
    )
    moderate_count = moderate_result.scalar()
    
    # Alertas por veículo
    alerts_by_vehicle_result = await db.execute(
        select(Vehicle.placa, func.count(Alert.id))
        .join(Alert, Alert.vehicle_id == Vehicle.id)
        .where(where_clause)
        .group_by(Vehicle.placa)
    )
    alerts_by_vehicle = {placa: count for placa, count in alerts_by_vehicle_result}
    
    # Alertas recentes (últimos 10)
    recent_alerts_result = await db.execute(
        select(Alert)
        .options(selectinload(Alert.vehicle))
        .where(where_clause)
        .order_by(desc(Alert.timestamp))
        .limit(10)
    )
    recent_alerts = recent_alerts_result.scalars().all()
    
    return {
        "total_alerts": total_alerts,
        "eyes_closed_count": eyes_closed_count,
        "yawning_count": yawning_count,
        "critical_count": critical_count,
        "moderate_count": moderate_count,
        "alerts_by_vehicle": alerts_by_vehicle,
        "recent_alerts": recent_alerts,
    }

