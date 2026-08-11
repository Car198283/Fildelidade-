from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Company
from app.services.dashboard_service import DashboardService
from app.services.pdf_service import PDFService
from app.utils.dependencies import get_current_user, get_effective_company_id

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def obter_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """ObtÃ©m estatÃ­sticas gerais (total clientes, premiados, inativos, aniversariantes)"""
    
    stats = DashboardService.get_dashboard_stats(db, company_id)
    
    return {
        "success": True,
        "data": stats
    }

@router.get("/top-customers")
def obter_top_clientes(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """ObtÃ©m TOP clientes por pontos"""
    
    customers = DashboardService.get_top_customers(db, company_id, limit)
    
    return {
        "success": True,
        "data": customers
    }

@router.get("/produtos-mais-vendidos")
def obter_produtos_mais_vendidos(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """Obtem produtos mais consumidos nos lancamentos de pontos"""

    produtos = DashboardService.get_produtos_mais_vendidos(db, company_id, limit)
    return {
        "success": True,
        "data": produtos
    }

@router.get("/clientes/{cliente_id}/produtos-consumidos")
def obter_produtos_consumidos_cliente(
    cliente_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """Obtem produtos consumidos por um cliente especifico"""

    produtos = DashboardService.get_produtos_consumidos_cliente(
        db,
        company_id,
        cliente_id,
        limit
    )
    return {
        "success": True,
        "data": produtos
    }

@router.get("/clientes-inativos")
def obter_clientes_inativos(
    dias: int = Query(15, ge=1, le=365),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """ObtÃ©m clientes que nÃ£o compram hÃ¡ X dias"""
    
    clientes = DashboardService.get_clientes_inativos(db, company_id, dias, limit)
    
    return {
        "success": True,
        "total": len(clientes),
        "dias_limite": dias,
        "data": clientes
    }

@router.get("/aniversariantes")
def obter_aniversariantes(
    mes: int = Query(None, ge=1, le=12),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """ObtÃ©m clientes aniversariantes do mÃªs (ou mÃªs especÃ­fico)"""
    
    clientes = DashboardService.get_aniversariantes(db, company_id, mes, limit)
    
    return {
        "success": True,
        "total": len(clientes),
        "mes": mes or "atual",
        "data": clientes
    }

@router.get("/aniversariantes-dia")
def obter_aniversariantes_dia(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """Obtem clientes aniversariantes do dia."""

    clientes = DashboardService.get_aniversariantes_dia(db, company_id, limit)

    return {
        "success": True,
        "total": len(clientes),
        "data": clientes
    }

@router.get("/clientes-premiados")
def obter_clientes_premiados(
    percentual_minimo: float = Query(80, ge=0, le=100),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """ObtÃ©m clientes com saldo >= percentual mÃ­nimo"""
    
    clientes = DashboardService.get_clientes_premiados(db, company_id, percentual_minimo, limit)
    
    return {
        "success": True,
        "total": len(clientes),
        "percentual_minimo": percentual_minimo,
        "data": clientes
    }

@router.get("/clientes-quase-premiados")
def obter_clientes_quase_premiados(
    percentual_min: float = Query(80, ge=0, le=100),
    percentual_max: float = Query(99.9, ge=0, le=100),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """ObtÃ©m clientes que estÃ£o entre 80% e 99.9% da meta (quase premiados)"""
    
    clientes = DashboardService.get_clientes_quase_premiados(db, company_id, percentual_min, percentual_max, limit)
    
    return {
        "success": True,
        "total": len(clientes),
        "percentual_min": percentual_min,
        "percentual_max": percentual_max,
        "data": clientes
    }

@router.get("/clientes-premiados-completo")
def obter_clientes_premiados_completo(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """ObtÃ©m clientes 100% premiados com informaÃ§Ãµes completas"""
    
    clientes = DashboardService.get_clientes_premiados_completo(db, company_id, limit)
    
    return {
        "success": True,
        "total": len(clientes),
        "data": clientes
    }

@router.get("/relatorio-pdf-aniversariantes")
def download_relatorio_aniversariantes(
    mes: int = Query(None, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """Download: RelatÃ³rio de aniversariantes em PDF"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    company_name = company.nome if company else "Fidelidade Total"
    
    pdf_buffer = PDFService.gerar_pdf_aniversariantes(
        db, company_id, company_name, mes
    )
    
    filename = f"aniversariantes_{datetime.now().strftime('%d_%m_%Y')}.pdf"
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/relatorio-pdf-premiados")
def download_relatorio_premiados(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """Download: RelatÃ³rio de clientes premiados (80%) em PDF"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    company_name = company.nome if company else "Fidelidade Total"
    
    pdf_buffer = PDFService.gerar_pdf_clientes_premiados(
        db, company_id, company_name
    )
    
    filename = f"clientes_premiados_{datetime.now().strftime('%d_%m_%Y')}.pdf"
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/relatorio-pdf-inativos")
def download_relatorio_inativos(
    dias: int = Query(15, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_effective_company_id)
):
    """Download: RelatÃ³rio de clientes inativos em PDF"""
    
    company = db.query(Company).filter(Company.id == company_id).first()
    company_name = company.nome if company else "Fidelidade Total"
    
    pdf_buffer = PDFService.gerar_pdf_clientes_inativos(
        db, company_id, company_name, dias
    )
    
    filename = f"clientes_inativos_{datetime.now().strftime('%d_%m_%Y')}.pdf"
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )