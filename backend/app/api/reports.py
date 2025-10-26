"""
Endpoints para geração de relatórios
"""
import os
import io
from datetime import datetime
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from .. import crud
from ..report_generator import generate_pdf_report, generate_excel_report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/export")
async def export_report(
    format: str = Query(..., regex="^(pdf|excel)$", description="Formato: pdf ou excel"),
    date_from: Optional[datetime] = Query(None, description="Data inicial"),
    date_to: Optional[datetime] = Query(None, description="Data final"),
    vehicle_id: Optional[UUID] = Query(None, description="ID do veículo"),
    include_images: bool = Query(False, description="Incluir imagens no relatório"),
    db: AsyncSession = Depends(get_db)
):
    """
    Exporta relatório em PDF ou Excel
    """
    # Buscar alertas com filtros
    alerts, total = await crud.get_alerts(
        db,
        skip=0,
        limit=10000,  # Limite alto para pegar todos os resultados
        vehicle_id=vehicle_id,
        date_from=date_from,
        date_to=date_to
    )
    
    if not alerts:
        raise HTTPException(
            status_code=404,
            detail="Nenhum alerta encontrado para os filtros especificados"
        )
    
    # Buscar informações do veículo se especificado
    vehicle = None
    if vehicle_id:
        vehicle = await crud.get_vehicle(db, vehicle_id)
    
    # Gerar relatório
    if format == "pdf":
        buffer = generate_pdf_report(
            alerts=alerts,
            vehicle=vehicle,
            date_from=date_from,
            date_to=date_to,
            include_images=include_images
        )
        
        filename = f"relatorio_fadiga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        media_type = "application/pdf"
    
    else:  # excel
        buffer = generate_excel_report(
            alerts=alerts,
            vehicle=vehicle,
            date_from=date_from,
            date_to=date_to
        )
        
        filename = f"relatorio_fadiga_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    # Retornar arquivo
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

