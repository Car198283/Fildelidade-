from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PromotionConfig, User
from app.schemas.schemas import PromotionConfigCreate, PromotionConfigUpdate
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/promocoes", tags=["Promotions"])

VALID_TYPES = {"quantidade", "valor", "percentual", "personalizada"}


def serialize_promocao(promocao: PromotionConfig) -> dict:
    tipo = promocao.tipo.value if hasattr(promocao.tipo, "value") else promocao.tipo

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
        if not body.descricao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para promocao personalizada, forneca uma descricao",
            )


@router.post("/config", response_model=dict)
def criar_promocao(
    body: PromotionConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria nova configuracao de promocao para a empresa."""

    validate_promocao(body)

    promocao = PromotionConfig(
        company_id=current_user.company_id,
        tipo=body.tipo,
        quantidade_produtos=body.quantidade_produtos,
        pontos_por_quantidade=body.pontos_por_quantidade,
        valor_gasto=body.valor_gasto,
        pontos_por_valor=body.pontos_por_valor,
        percentual=body.percentual,
        descricao=body.descricao,
        ativo=body.ativo,
    )
    db.add(promocao)
    db.commit()
    db.refresh(promocao)

    return {"success": True, "data": serialize_promocao(promocao)}


@router.get("/config", response_model=dict)
def obter_promocao(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtem a promocao ativa mais recente da empresa."""

    promocao = (
        db.query(PromotionConfig)
        .filter(
            PromotionConfig.company_id == current_user.company_id,
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
    current_user: User = Depends(get_current_user),
):
    """Lista todas as configuracoes de promocao da empresa."""

    promocoes = (
        db.query(PromotionConfig)
        .filter(PromotionConfig.company_id == current_user.company_id)
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
    current_user: User = Depends(get_current_user),
):
    """Atualiza configuracao de promocao."""

    promocao = (
        db.query(PromotionConfig)
        .filter(
            PromotionConfig.id == promocao_id,
            PromotionConfig.company_id == current_user.company_id,
        )
        .first()
    )

    if not promocao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuracao de promocao nao encontrada",
        )

    if body.tipo is not None:
        validate_promocao(body)
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

    db.commit()
    db.refresh(promocao)

    return {"success": True, "data": serialize_promocao(promocao)}
