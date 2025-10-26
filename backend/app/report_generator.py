"""
Geração de relatórios em PDF e Excel
"""
import io
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows

from .models import Alert, Vehicle


def generate_pdf_report(
    alerts: List[Alert],
    vehicle: Optional[Vehicle] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    include_images: bool = False
) -> io.BytesIO:
    """
    Gera relatório em PDF com os alertas de fadiga
    """
    buffer = io.BytesIO()
    
    # Criar documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4) if not include_images else A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilo customizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1976D2'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Título
    title = Paragraph("Relatório de Detecção de Fadiga", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Informações do relatório
    info_style = styles['Normal']
    info_data = [
        ["Gerado em:", datetime.now().strftime("%d/%m/%Y às %H:%M:%S")],
        ["Total de alertas:", str(len(alerts))],
    ]
    
    if vehicle:
        info_data.extend([
            ["Veículo:", vehicle.nome],
            ["Placa:", vehicle.placa],
        ])
    
    if date_from:
        info_data.append(["Período inicial:", date_from.strftime("%d/%m/%Y %H:%M")])
    if date_to:
        info_data.append(["Período final:", date_to.strftime("%d/%m/%Y %H:%M")])
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Tabela de alertas
    if not include_images:
        # Modo compacto: apenas tabela
        table_data = [["Data/Hora", "Veículo", "Placa", "Tipo", "Severidade", "EAR", "MAR"]]
        
        for alert in alerts:
            tipo_map = {"eyes_closed": "Olhos Fechados", "yawning": "Bocejo"}
            severity_map = {"critical": "Crítico", "moderate": "Moderado"}
            
            table_data.append([
                alert.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
                alert.vehicle.nome if alert.vehicle else "N/A",
                alert.vehicle.placa if alert.vehicle else "N/A",
                tipo_map.get(alert.tipo.value, alert.tipo.value),
                severity_map.get(alert.severity.value, alert.severity.value),
                f"{alert.ear_value:.3f}",
                f"{alert.mar_value:.3f}",
            ])
        
        alerts_table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1.2*inch, 1*inch, 0.7*inch, 0.7*inch])
        alerts_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(alerts_table)
    
    else:
        # Modo com imagens: um alerta por página
        uploads_dir = Path(__file__).parent.parent.parent / "uploads"
        
        for i, alert in enumerate(alerts):
            if i > 0:
                elements.append(PageBreak())
            
            # Informações do alerta
            tipo_map = {"eyes_closed": "Olhos Fechados", "yawning": "Bocejo"}
            severity_map = {"critical": "Crítico", "moderate": "Moderado"}
            
            alert_title = Paragraph(f"Alerta #{i+1}", styles['Heading2'])
            elements.append(alert_title)
            elements.append(Spacer(1, 12))
            
            alert_data = [
                ["Data/Hora:", alert.timestamp.strftime("%d/%m/%Y às %H:%M:%S")],
                ["Veículo:", alert.vehicle.nome if alert.vehicle else "N/A"],
                ["Placa:", alert.vehicle.placa if alert.vehicle else "N/A"],
                ["Tipo:", tipo_map.get(alert.tipo.value, alert.tipo.value)],
                ["Severidade:", severity_map.get(alert.severity.value, alert.severity.value)],
                ["EAR:", f"{alert.ear_value:.3f}"],
                ["MAR:", f"{alert.mar_value:.3f}"],
            ]
            
            alert_table = Table(alert_data, colWidths=[2*inch, 4*inch])
            alert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(alert_table)
            elements.append(Spacer(1, 20))
            
            # Imagem se disponível
            if alert.image_path:
                image_path = uploads_dir / alert.image_path.replace("/uploads/", "")
                if image_path.exists():
                    try:
                        img = Image(str(image_path), width=5*inch, height=3.75*inch)
                        elements.append(img)
                    except:
                        elements.append(Paragraph("Imagem não disponível", styles['Normal']))
                else:
                    elements.append(Paragraph("Imagem não encontrada", styles['Normal']))
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_excel_report(
    alerts: List[Alert],
    vehicle: Optional[Vehicle] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> io.BytesIO:
    """
    Gera relatório em Excel com os alertas de fadiga
    """
    # Preparar dados
    data = []
    tipo_map = {"eyes_closed": "Olhos Fechados", "yawning": "Bocejo"}
    severity_map = {"critical": "Crítico", "moderate": "Moderado"}
    
    for alert in alerts:
        data.append({
            "Data/Hora": alert.timestamp.strftime("%d/%m/%Y %H:%M:%S"),
            "Veículo": alert.vehicle.nome if alert.vehicle else "N/A",
            "Placa": alert.vehicle.placa if alert.vehicle else "N/A",
            "Motorista": alert.vehicle.motorista if alert.vehicle and alert.vehicle.motorista else "N/A",
            "Tipo": tipo_map.get(alert.tipo.value, alert.tipo.value),
            "Severidade": severity_map.get(alert.severity.value, alert.severity.value),
            "EAR": alert.ear_value,
            "MAR": alert.mar_value,
        })
    
    df = pd.DataFrame(data)
    
    # Criar workbook
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Alertas', index=False)
        
        # Formatação
        workbook = writer.book
        worksheet = writer.sheets['Alertas']
        
        # Estilo do cabeçalho
        header_fill = PatternFill(start_color="1976D2", end_color="1976D2", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Ajustar largura das colunas
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # Adicionar informações do relatório em outra aba
        info_sheet = workbook.create_sheet("Informações")
        info_sheet['A1'] = "Relatório de Detecção de Fadiga"
        info_sheet['A1'].font = Font(bold=True, size=14)
        
        info_sheet['A3'] = "Gerado em:"
        info_sheet['B3'] = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        
        info_sheet['A4'] = "Total de alertas:"
        info_sheet['B4'] = len(alerts)
        
        if vehicle:
            info_sheet['A5'] = "Veículo:"
            info_sheet['B5'] = f"{vehicle.nome} ({vehicle.placa})"
        
        if date_from:
            info_sheet['A6'] = "Período inicial:"
            info_sheet['B6'] = date_from.strftime("%d/%m/%Y %H:%M")
        
        if date_to:
            info_sheet['A7'] = "Período final:"
            info_sheet['B7'] = date_to.strftime("%d/%m/%Y %H:%M")
    
    buffer.seek(0)
    return buffer

