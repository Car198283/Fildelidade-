from datetime import date, datetime, time, timedelta
from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company, Customer, PointsTransaction, Product, ReportExportAudit, User
from app.utils.dependencies import require_master

router = APIRouter(prefix="/admin/reports", tags=["Master Reports"])

REPORT_NAMES = {
    "compras": "Compras",
    "clientes": "Clientes",
    "pontos": "Movimentacoes de pontos",
    "premiacoes": "Premiacoes e resgates",
    "produtos": "Produtos",
    "empresas": "Empresas",
    "usuarios": "Usuarios",
}


def _date_limits(start_date: date | None, end_date: date | None):
    start = datetime.combine(start_date, time.min) if start_date else None
    end = datetime.combine(end_date + timedelta(days=1), time.min) if end_date else None
    return start, end


def _apply_period(query, column, start, end):
    if start:
        query = query.filter(column >= start)
    if end:
        query = query.filter(column < end)
    return query


def _clean(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    if hasattr(value, "as_integer_ratio"):
        return float(value)
    return value


def build_report(db: Session, report_type: str, company_id: int | None, start_date: date | None, end_date: date | None):
    if report_type not in REPORT_NAMES:
        raise HTTPException(status_code=404, detail="Tipo de relatorio invalido")
    start, end = _date_limits(start_date, end_date)

    if report_type in {"compras", "pontos", "premiacoes"}:
        query = db.query(
            PointsTransaction.created_at.label("Data"),
            Company.nome.label("Empresa"),
            Customer.nome.label("Cliente"),
            Customer.telefone.label("Telefone"),
            PointsTransaction.product_nome.label("Produto"),
            PointsTransaction.valor_compra.label("Valor"),
            PointsTransaction.tipo.label("Tipo"),
            PointsTransaction.pontos.label("Pontos"),
            User.nome.label("Operador"),
            PointsTransaction.descricao.label("Descricao"),
        ).join(Company, Company.id == PointsTransaction.company_id).join(
            Customer, Customer.id == PointsTransaction.customer_id
        ).outerjoin(User, User.id == PointsTransaction.user_id)
        if report_type == "compras":
            query = query.filter(PointsTransaction.tipo == "entrada", PointsTransaction.valor_compra.isnot(None))
        elif report_type == "premiacoes":
            query = query.filter(PointsTransaction.tipo == "saida")
        if company_id:
            query = query.filter(PointsTransaction.company_id == company_id)
        query = _apply_period(query, PointsTransaction.created_at, start, end)
        rows = query.order_by(PointsTransaction.created_at.desc()).all()

    elif report_type == "clientes":
        query = db.query(
            Customer.created_at.label("Cadastro"), Company.nome.label("Empresa"), Customer.nome.label("Cliente"),
            Customer.telefone.label("Telefone"), Customer.email.label("Email"), Customer.pontos.label("Saldo de pontos"),
            Customer.valor_gasto_atual.label("Valor acumulado"), Customer.quantidade_produtos_comprados.label("Produtos comprados"),
            Customer.ativo.label("Ativo"),
        ).join(Company, Company.id == Customer.company_id)
        if company_id:
            query = query.filter(Customer.company_id == company_id)
        query = _apply_period(query, Customer.created_at, start, end)
        rows = query.order_by(Customer.nome).all()

    elif report_type == "produtos":
        query = db.query(
            Company.nome.label("Empresa"), Product.nome.label("Produto"), Product.preco.label("Preco"),
            func.count(PointsTransaction.id).label("Vendas"),
            func.coalesce(func.sum(PointsTransaction.valor_compra), 0).label("Faturamento"),
            func.coalesce(func.sum(PointsTransaction.pontos), 0).label("Pontos gerados"),
        ).join(Company, Company.id == Product.company_id).outerjoin(
            PointsTransaction,
            (PointsTransaction.product_id == Product.id) & (PointsTransaction.tipo == "entrada"),
        )
        if company_id:
            query = query.filter(Product.company_id == company_id)
        if start:
            query = query.filter((PointsTransaction.created_at >= start) | (PointsTransaction.id.is_(None)))
        if end:
            query = query.filter((PointsTransaction.created_at < end) | (PointsTransaction.id.is_(None)))
        rows = query.group_by(Company.nome, Product.id, Product.nome, Product.preco).order_by(Company.nome, Product.nome).all()

    elif report_type == "empresas":
        query = db.query(
            Company.created_at.label("Cadastro"), Company.nome.label("Empresa"), Company.cnpj.label("CNPJ"),
            Company.plano.label("Plano"), Company.ativo.label("Ativa"), Company.read_only.label("Somente leitura"),
            func.count(func.distinct(Customer.id)).label("Clientes"),
            func.count(func.distinct(User.id)).label("Usuarios"),
        ).outerjoin(Customer, Customer.company_id == Company.id).outerjoin(User, User.company_id == Company.id)
        if company_id:
            query = query.filter(Company.id == company_id)
        query = _apply_period(query, Company.created_at, start, end)
        rows = query.group_by(Company.id).order_by(Company.nome).all()

    else:
        query = db.query(
            User.created_at.label("Cadastro"), Company.nome.label("Empresa"), User.nome.label("Usuario"),
            User.email.label("Email"), User.role.label("Perfil"), User.ativo.label("Ativo"),
            User.ultimo_acesso.label("Ultimo acesso"), User.exigir_troca_senha.label("Troca de senha pendente"),
        ).join(Company, Company.id == User.company_id).filter(User.excluido_em.is_(None))
        if company_id:
            query = query.filter(User.company_id == company_id)
        query = _apply_period(query, User.created_at, start, end)
        rows = query.order_by(Company.nome, User.nome, User.email).all()

    columns = list(rows[0]._mapping.keys()) if rows else []
    return columns, [{column: _clean(row._mapping[column]) for column in columns} for row in rows]


@router.get("/preview")
def preview_report(
    report_type: str,
    company_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_master),
):
    columns, rows = build_report(db, report_type, company_id, start_date, end_date)
    return {"success": True, "data": {"columns": columns, "rows": rows[:100], "total": len(rows)}}


@router.get("/export")
def export_report(
    report_type: str,
    format: str = Query("xlsx", pattern="^(xlsx|pdf)$"),
    company_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master),
):
    columns, rows = build_report(db, report_type, company_id, start_date, end_date)
    if not rows:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado para os filtros informados")
    db.add(ReportExportAudit(
        user_id=current_user.id,
        company_id=company_id,
        report_type=report_type,
        export_format=format,
        filters={
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "total_rows": len(rows),
        },
    ))
    db.commit()
    title = REPORT_NAMES[report_type]
    filename = f"relatorio_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if format == "xlsx":
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            frame = pd.DataFrame(rows, columns=columns)
            frame.to_excel(writer, sheet_name=title[:31], index=False)
            sheet = writer.sheets[title[:31]]
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions
            for cells in sheet.columns:
                width = min(max(len(str(cell.value or "")) for cell in cells) + 2, 45)
                sheet.column_dimensions[cells[0].column_letter].width = width
        output.seek(0)
        return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": f'attachment; filename="{filename}.xlsx"'})

    output = BytesIO()
    document = SimpleDocTemplate(output, pagesize=landscape(A4), leftMargin=0.8 * cm, rightMargin=0.8 * cm, topMargin=0.8 * cm, bottomMargin=0.8 * cm)
    styles = getSampleStyleSheet()
    body = [Paragraph(f"<b>Fidelidade Total - {title}</b>", styles["Title"]), Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} | {len(rows)} registro(s)", styles["Normal"]), Spacer(1, 0.4 * cm)]
    table_data = [columns] + [[str(row[column]) for column in columns] for row in rows]
    table = Table(table_data, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4f46e5")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 6.5),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    body.append(table)
    document.build(body)
    output.seek(0)
    return StreamingResponse(output, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}.pdf"'})
