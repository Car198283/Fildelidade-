from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from types import SimpleNamespace

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PromotionAudit, PromotionConfig, User
from app.schemas.schemas import PromotionConfigCreate, PromotionConfigUpdate, PromotionSimulation
from app.utils.dependencies import get_effective_company_id, get_writable_company_id, require_admin_or_master

router = APIRouter(prefix="/promocoes", tags=["Promotions"])

VALID_TYPES = {"quantidade", "valor", "percentual", "personalizada"}


def serialize_promocao(promocao: PromotionConfig) -> dict:
    tipo = promocao.tipo.value if hasattr(promocao.tipo, "value") else promocao.tipo

    now = datetime.now()
    if promocao.data_inicio and promocao.data_inicio > now:
        situacao = "agendada"
    elif promocao.data_fim and promocao.data_fim < now:
        situacao = "encerrada"
    elif not promocao.ativo:
        situacao = "pausada"
    else:
        situacao = "ativa"

    return {
        "id": promocao.id,
        "tipo": tipo,
        "quantidade_produtos": promocao.quantidade_produtos,
        "pontos_por_quantidade": promocao.pontos_por_quantidade,
        "valor_gasto": promocao.valor_gasto,
        "pontos_por_valor": promocao.pontos_por_valor,
        "percentual": promocao.percentual,
        "descricao": promocao.descricao,
        "ativo": promocao.ativo,
        "situacao": situacao,
        "nome": promocao.nome,
        "data_inicio": promocao.data_inicio,
        "data_fim": promocao.data_fim,
        "acumulavel": promocao.acumulavel,
        "prioridade": promocao.prioridade,
        "limite_por_cliente": promocao.limite_por_cliente,
        "limite_total": promocao.limite_total,
        "valor_minimo_compra": promocao.valor_minimo_compra,
        "recompensa_tipo": promocao.recompensa_tipo,
        "recompensa_valor": promocao.recompensa_valor,
        "condicao_campo": promocao.condicao_campo,
        "condicao_operador": promocao.condicao_operador,
        "condicao_valor": promocao.condicao_valor,
        "produtos_elegiveis": promocao.produtos_elegiveis,
        "categorias_elegiveis": promocao.categorias_elegiveis,
        "motivo_alteracao": promocao.motivo_alteracao,
        "created_at": promocao.created_at,
    }


def validate_promocao(body) -> None:
    if body.tipo not in VALID_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Tipo de promocao invalido. Use: quantidade, valor, "
                "percentual ou personalizada"
            ),
        )

    if body.tipo == "quantidade":
        if body.quantidade_produtos is None or body.pontos_por_quantidade is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Para promocao por quantidade, forneca "
                    "quantidade_produtos e pontos_por_quantidade"
                ),
            )
    elif body.tipo == "valor":
        if body.valor_gasto is None or body.pontos_por_valor is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para promocao por valor, forneca valor_gasto e pontos_por_valor",
            )
    elif body.tipo == "percentual":
        if body.percentual is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para promocao percentual, forneca percentual",
            )
    elif body.tipo == "personalizada":
        if not body.descricao or not body.condicao_campo or not body.condicao_operador:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Promocao personalizada exige descricao, campo e operador",
            )
    if body.data_inicio and body.data_fim and body.data_fim <= body.data_inicio:
        raise HTTPException(status_code=400, detail="Data final deve ser posterior a data inicial")


ADVANCED_FIELDS = (
    "nome", "data_inicio", "data_fim", "acumulavel", "prioridade",
    "limite_por_cliente", "limite_total", "valor_minimo_compra",
    "recompensa_tipo", "recompensa_valor", "condicao_campo",
    "condicao_operador", "condicao_valor", "produtos_elegiveis",
    "categorias_elegiveis", "motivo_alteracao",
)


def audit(db, promocao, user_id, acao, motivo, antes=None):
    db.add(PromotionAudit(
        promotion_id=promocao.id, company_id=promocao.company_id, user_id=user_id,
        acao=acao, motivo=motivo, antes=jsonable_encoder(antes),
        depois=jsonable_encoder(serialize_promocao(promocao)),
    ))


@router.post("/config", response_model=dict)
def criar_promocao(
    body: PromotionConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id),
):
    """Cria nova configuracao de promocao para a empresa."""

    validate_promocao(body)

    promocao = PromotionConfig(
        company_id=company_id,
        tipo=body.tipo,
        quantidade_produtos=body.quantidade_produtos,
        pontos_por_quantidade=body.pontos_por_quantidade,
        valor_gasto=body.valor_gasto,
        pontos_por_valor=body.pontos_por_valor,
        percentual=body.percentual,
        descricao=body.descricao,
        ativo=body.ativo,
        **{field: getattr(body, field) for field in ADVANCED_FIELDS},
    )
    db.add(promocao)
    db.flush()
    audit(db, promocao, current_user.id, "criacao", body.motivo_alteracao)
    db.commit()
    db.refresh(promocao)

    return {"success": True, "data": serialize_promocao(promocao)}


@router.get("/config", response_model=dict)
def obter_promocao(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_effective_company_id),
):
    """Obtem a promocao ativa mais recente da empresa."""

    promocao = (
        db.query(PromotionConfig)
        .filter(
            PromotionConfig.company_id == company_id,
            PromotionConfig.ativo == True,
        )
        .order_by(PromotionConfig.id.desc())
        .first()
    )

    if not promocao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma configuracao de promocao ativa encontrada",
        )

    return {"success": True, "data": serialize_promocao(promocao)}


@router.get("/configs", response_model=dict)
def listar_promocoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_effective_company_id),
):
    """Lista todas as configuracoes de promocao da empresa."""

    promocoes = (
        db.query(PromotionConfig)
        .filter(PromotionConfig.company_id == company_id)
        .order_by(PromotionConfig.id.desc())
        .all()
    )

    return {
        "success": True,
        "total": len(promocoes),
        "data": [serialize_promocao(promocao) for promocao in promocoes],
    }


@router.put("/config/{promocao_id}", response_model=dict)
def atualizar_promocao(
    promocao_id: int,
    body: PromotionConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id),
):
    """Atualiza configuracao de promocao."""

    promocao = (
        db.query(PromotionConfig)
        .filter(
            PromotionConfig.id == promocao_id,
            PromotionConfig.company_id == company_id,
        )
        .first()
    )

    if not promocao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuracao de promocao nao encontrada",
        )

    antes = serialize_promocao(promocao)
    if body.tipo is not None:
        promocao.tipo = body.tipo
    if body.quantidade_produtos is not None:
        promocao.quantidade_produtos = body.quantidade_produtos
    if body.pontos_por_quantidade is not None:
        promocao.pontos_por_quantidade = body.pontos_por_quantidade
    if body.valor_gasto is not None:
        promocao.valor_gasto = body.valor_gasto
    if body.pontos_por_valor is not None:
        promocao.pontos_por_valor = body.pontos_por_valor
    if body.percentual is not None:
        promocao.percentual = body.percentual
    if body.descricao is not None:
        promocao.descricao = body.descricao
    if body.ativo is not None:
        promocao.ativo = body.ativo
    for field in ADVANCED_FIELDS:
        value = getattr(body, field)
        if value is not None:
            setattr(promocao, field, value)

    validate_promocao(SimpleNamespace(**serialize_promocao(promocao)))

    audit(db, promocao, current_user.id, "atualizacao", body.motivo_alteracao, antes)

    db.commit()
    db.refresh(promocao)

    return {"success": True, "data": serialize_promocao(promocao)}


@router.get("/historico", response_model=dict)
def historico_promocoes(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_effective_company_id),
):
    rows = db.query(PromotionAudit).filter(PromotionAudit.company_id == company_id).order_by(PromotionAudit.created_at.desc()).limit(100).all()
    return {"success": True, "data": [{"id": row.id, "promotion_id": row.promotion_id, "user_id": row.user_id, "acao": row.acao, "motivo": row.motivo, "antes": row.antes, "depois": row.depois, "created_at": row.created_at} for row in rows]}


@router.post("/simular", response_model=dict)
def simular_promocoes(
    body: PromotionSimulation,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_effective_company_id),
):
    now = datetime.now()
    rows = db.query(PromotionConfig).filter(PromotionConfig.company_id == company_id, PromotionConfig.ativo == True).order_by(PromotionConfig.prioridade.desc()).all()
    results, total_points = [], 0.0
    for row in rows:
        if row.data_inicio and row.data_inicio > now: continue
        if row.data_fim and row.data_fim < now: continue
        points = 0.0
        tipo = row.tipo.value if hasattr(row.tipo, "value") else row.tipo
        if tipo == "quantidade" and row.quantidade_produtos:
            points = (body.compras // row.quantidade_produtos) * float(row.pontos_por_quantidade or 0)
        elif tipo == "valor" and row.valor_gasto:
            points = int(body.valor_compra // float(row.valor_gasto)) * float(row.pontos_por_valor or 0)
        elif tipo == "percentual":
            points = body.valor_compra * float(row.percentual or 0) / 100
        elif tipo == "personalizada":
            actual = body.valor_compra if row.condicao_campo == "valor_compra" else body.compras
            expected = float(row.condicao_valor or 0)
            matches = {
                ">=": actual >= expected,
                "=": actual == expected,
                "<=": actual <= expected,
            }.get(row.condicao_operador, False)
            if matches and row.recompensa_tipo == "pontos":
                points = float(row.recompensa_valor or 0)
        if body.valor_compra < float(row.valor_minimo_compra or 0): points = 0
        results.append({"id": row.id, "nome": row.nome or str(tipo), "pontos": round(points, 2), "recompensa_tipo": row.recompensa_tipo})
        total_points += points
        if points and not row.acumulavel: break
    return {"success": True, "data": {"pontos_totais": round(total_points, 2), "regras": results}}
