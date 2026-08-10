from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Company
from app.services.pdf_service import PDFService
from app.utils.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/relatorios", tags=["Reports"])

@router.get("/aniversariantes/pdf")
def baixar_pdf_aniversariantes(
    mes: int = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Baixa PDF com aniversariantes do mês"""
    
    # Obter nome da empresa
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    company_name = company.nome if company else "Empresa"
    
    # Gerar PDF
    pdf_buffer = PDFService.gerar_pdf_aniversariantes(db, current_user.company_id, company_name, mes)
    
    mes_nome = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho",
               "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    mes_atual = mes or datetime.now().month
    filename = f"aniversariantes_{mes_nome[mes_atual - 1]}_{datetime.now().strftime('%d%m%Y')}.pdf"
    
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/premiados/pdf")
def baixar_pdf_clientes_premiados(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Baixa PDF com clientes premiados (80%)"""
    
    # Obter nome da empresa
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    company_name = company.nome if company else "Empresa"
    
    # Gerar PDF
    pdf_buffer = PDFService.gerar_pdf_clientes_premiados(db, current_user.company_id, company_name)
    
    filename = f"clientes_premiados_{datetime.now().strftime('%d%m%Y')}.pdf"
    
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/inativos/pdf")
def baixar_pdf_clientes_inativos(
    dias: int = Query(15, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Baixa PDF com clientes inativos"""
    
    # Obter nome da empresa
    company = db.query(Company).filter(Company.id == current_user.company_id).first()
    company_name = company.nome if company else "Empresa"
    
    # Gerar PDF
    pdf_buffer = PDFService.gerar_pdf_clientes_inativos(db, current_user.company_id, company_name, dias)
    
    filename = f"clientes_inativos_{dias}dias_{datetime.now().strftime('%d%m%Y')}.pdf"
    
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
