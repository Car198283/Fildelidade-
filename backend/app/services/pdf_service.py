from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from app.services.dashboard_service import DashboardService

class PDFService:
    """Serviço para gerar relatórios em PDF"""
    
    @staticmethod
    def gerar_pdf_aniversariantes(db: Session, company_id: int, company_name: str, mes: int = None) -> BytesIO:
        """Gera PDF com lista de aniversariantes do mês"""
        
        # Obter dados
        aniversariantes = DashboardService.get_aniversariantes(db, company_id, mes)
        
        # Criar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=10, bottomMargin=10)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            alignment=TA_LEFT
        )
        
        # Conteúdo
        story = []
        story.append(Paragraph(f"RELATÓRIO DE ANIVERSARIANTES - {company_name}", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Data do relatório
        mes_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                   "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        mes_atual = mes or datetime.now().month
        story.append(Paragraph(f"<b>Mês:</b> {mes_nome[mes_atual - 1]} | <b>Data:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                               header_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Tabela de aniversariantes
        data = [["ID", "Nome", "Data de Nascimento", "Idade", "Pontos", "Telefone"]]
        
        for cliente in aniversariantes:
            data.append([
                str(cliente.get("id")),
                cliente.get("nome", ""),
                cliente.get("data_nascimento", ""),
                str(cliente.get("idade", "")),
                f"{cliente.get('pontos', 0):.2f}",
                cliente.get("telefone", "")
            ])
        
        # Tabela
        table = Table(data, colWidths=[0.8*inch, 2*inch, 1.5*inch, 0.8*inch, 1*inch, 1.4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(f"<b>Total:</b> {len(aniversariantes)} aniversariante(s)", header_style))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def gerar_pdf_clientes_premiados(db: Session, company_id: int, company_name: str) -> BytesIO:
        """Gera PDF com lista de clientes premiados (80%)"""
        
        # Obter dados
        premiados = DashboardService.get_clientes_premiados(db, company_id, 80)
        
        # Criar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=10, bottomMargin=10)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#00cc00'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            alignment=TA_LEFT
        )
        
        # Conteúdo
        story = []
        story.append(Paragraph(f"RELATÓRIO DE CLIENTES PREMIADOS - {company_name}", title_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"<b>Clientes com 80% ou mais de pontos</b> | <b>Data:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                               header_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Tabela
        data = [["ID", "Nome", "Pontos", "Telefone", "Email", "Data de Cadastro"]]
        
        for cliente in premiados:
            data.append([
                str(cliente.get("id")),
                cliente.get("nome", ""),
                f"{cliente.get('pontos', 0):.2f}",
                cliente.get("telefone", ""),
                cliente.get("email", ""),
                datetime.fromisoformat(str(cliente.get("created_at"))).strftime('%d/%m/%Y') if cliente.get("created_at") else ""
            ])
        
        table = Table(data, colWidths=[0.8*inch, 2*inch, 1*inch, 1.4*inch, 1.8*inch, 1.4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00cc00')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')])
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(f"<b>Total:</b> {len(premiados)} cliente(s) premiado(s)", header_style))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def gerar_pdf_clientes_inativos(db: Session, company_id: int, company_name: str, dias: int = 15) -> BytesIO:
        """Gera PDF com lista de clientes inativos"""
        
        try:
            # Obter dados
            inativos = DashboardService.get_clientes_inativos(db, company_id, dias)
        except:
            inativos = []
        
        # Criar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=10, bottomMargin=10)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#ff6600'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            alignment=TA_LEFT
        )
        
        # Conteúdo
        story = []
        story.append(Paragraph(f"RELATÓRIO DE CLIENTES INATIVOS - {company_name}", title_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"<b>Clientes sem compras há {dias} dias ou mais</b> | <b>Data:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                               header_style))
        story.append(Spacer(1, 0.2 * inch))
        
        if not inativos:
            # Se vazio, mostrar mensagem
            story.append(Paragraph("<b>Nenhum cliente inativo encontrado neste período.</b>", header_style))
        else:
            # Tabela
            data = [["ID", "Nome", "Pontos", "Telefone", "Email", "Data de Cadastro"]]
            
            for cliente in inativos:
                data.append([
                    str(cliente.get("id", "")),
                    cliente.get("nome", ""),
                    f"{cliente.get('pontos', 0):.2f}",
                    cliente.get("telefone", ""),
                    cliente.get("email", ""),
                    datetime.fromisoformat(str(cliente.get("created_at"))).strftime('%d/%m/%Y') if cliente.get("created_at") else ""
                ])
            
            table = Table(data, colWidths=[0.8*inch, 2*inch, 1*inch, 1.4*inch, 1.8*inch, 1.4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6600')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff8e1')])
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph(f"<b>Total:</b> {len(inativos)} cliente(s) inativo(s)", header_style))
        
        # Gerar PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
