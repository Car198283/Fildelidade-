from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Company, Customer, PointsTransaction, Product, PromotionConfig, User, UserAudit, WhatsAppMessage
from app.schemas.schemas import ManagedCompanyCreate, ManagedCompanyUpdate, ManagedUserCreate, ManagedUserUpdate
from app.services.auth_service import AuthService
from app.utils.dependencies import (
    ROLE_ADMIN,
    ROLE_MASTER,
    get_current_user,
    is_master,
    require_admin_or_master,
    require_master,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


def serialize_company(company: Company) -> dict:
    return {
        "id": company.id,
        "nome": company.nome,
        "razao_social": company.razao_social,
        "cnpj": company.cnpj,
        "telefone": company.telefone,
        "email": company.email,
        "responsavel": company.responsavel,
        "cep": company.cep,
        "endereco": company.endereco,
        "numero": company.numero,
        "bairro": company.bairro,
        "cidade": company.cidade,
        "estado": company.estado,
        "logotipo": company.logotipo,
        "plano": company.plano,
        "ativo": company.ativo,
        "read_only": company.read_only,
        "created_at": company.created_at,
        "updated_at": company.updated_at,
    }


def serialize_user(user: User) -> dict:
    data = {
        "id": user.id,
        "email": user.email,
        "nome": user.nome,
        "company_id": user.company_id,
        "role": user.role,
        "ativo": user.ativo,
        "ultimo_acesso": user.ultimo_acesso,
        "exigir_troca_senha": user.exigir_troca_senha,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }
    if user.company:
        data["company_name"] = user.company.nome
        data["company_read_only"] = user.company.read_only
    return data


def resolve_company_id(current_user: User, requested_company_id: int | None) -> int:
    if is_master(current_user):
        return requested_company_id or current_user.company_id
    return current_user.company_id


def ensure_company_has_another_admin(db: Session, user: User) -> None:
    if user.role != ROLE_ADMIN or not user.ativo:
        return
    another = (
        db.query(User.id)
        .filter(
            User.company_id == user.company_id,
            User.role == ROLE_ADMIN,
            User.ativo == True,
            User.id != user.id,
        )
        .first()
    )
    if not another:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A empresa precisa manter pelo menos um administrador ativo",
        )


def audit_user(db: Session, target: User, actor: User, action: str, reason: str, details=None) -> None:
    db.add(UserAudit(
        target_user_id=target.id,
        actor_user_id=actor.id,
        company_id=target.company_id,
        acao=action,
        motivo=reason,
        detalhes=details,
    ))


@router.get("/companies")
def listar_empresas(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master),
):
    empresas = db.query(Company).order_by(Company.nome.asc()).all()
    return {"success": True, "data": [serialize_company(company) for company in empresas]}


@router.post("/companies", status_code=status.HTTP_201_CREATED)
def criar_empresa(
    body: ManagedCompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master),
):
    # tenant-scope: global - email e unico em todo o sistema.
    existing_user = db.query(User).filter(User.email == body.admin_email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email do administrador ja cadastrado")

    existing_company = db.query(Company).filter(Company.cnpj == body.cnpj).first()
    if existing_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CNPJ ja cadastrado")

    try:
        company = Company(
            nome=body.nome,
            razao_social=body.razao_social,
            cnpj=body.cnpj,
            telefone=body.telefone,
            email=str(body.email),
            responsavel=body.responsavel,
            cep=body.cep,
            endereco=body.endereco,
            numero=body.numero,
            bairro=body.bairro,
            cidade=body.cidade,
            estado=body.estado.upper() if body.estado else None,
            logotipo=body.logotipo,
            plano=body.plano,
            ativo=True,
            read_only=False,
        )
        db.add(company)
        db.flush()

        user = User(
            email=body.admin_email,
            senha_hash=AuthService.hash_password(body.admin_senha),
            company_id=company.id,
            role=ROLE_ADMIN,
            ativo=True,
        )
        db.add(user)

        promotion_config = PromotionConfig(
            company_id=company.id,
            tipo="quantidade",
            quantidade_produtos=10,
            pontos_por_quantidade=1,
            descricao="Promocao padrao inicial",
            ativo=True,
        )
        db.add(promotion_config)

        db.commit()
        db.refresh(company)
        db.refresh(user)
    except Exception:
        db.rollback()
        raise

    return {
        "success": True,
        "data": {
            "company": serialize_company(company),
            "admin": serialize_user(user),
        },
    }


@router.put("/companies/{company_id}")
def atualizar_empresa(
    company_id: int,
    body: ManagedCompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa nao encontrada")

    if company.id == current_user.company_id and body.ativo is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Master nao pode bloquear a propria empresa")

    if body.ativo is not None:
        company.ativo = body.ativo
        if body.ativo is False:
            company.read_only = False

    if body.read_only is not None:
        if body.read_only and company.id == current_user.company_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Master nao pode limitar a propria empresa")
        if body.read_only and not company.ativo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empresa bloqueada nao pode ficar somente leitura")
        company.read_only = body.read_only

    text_fields = [
        "razao_social",
        "nome",
        "cnpj",
        "telefone",
        "email",
        "responsavel",
        "cep",
        "endereco",
        "numero",
        "bairro",
        "cidade",
        "estado",
        "logotipo",
        "plano",
    ]
    for field in text_fields:
        value = getattr(body, field)
        if value is not None:
            if field == "cnpj":
                existing_company = (
                    db.query(Company)
                    .filter(Company.cnpj == value, Company.id != company.id)
                    .first()
                )
                if existing_company:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CNPJ ja cadastrado")
            if field == "estado":
                value = value.upper()
            if field == "email":
                value = str(value)
            setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return {"success": True, "data": serialize_company(company)}


@router.delete("/companies/{company_id}")
def excluir_empresa(
    company_id: int,
    force: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa nao encontrada")

    if company.id == current_user.company_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Master nao pode excluir a propria empresa")

    has_transactions = (
        db.query(PointsTransaction.id)
        .filter(PointsTransaction.company_id == company_id)
        .first()
        is not None
    )
    if has_transactions:
        if not force:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empresa possui movimentacoes. Escolha bloquear ou confirme excluir empresa e todos os dados.",
            )

    has_data = (
        db.query(Customer.id).filter(Customer.company_id == company_id).first()
        or db.query(Product.id).filter(Product.company_id == company_id).first()
        or db.query(WhatsAppMessage.id).filter(WhatsAppMessage.company_id == company_id).first()
    )
    if has_data and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empresa possui dados cadastrados. Escolha bloquear ou confirme excluir empresa e todos os dados.",
        )

    db.delete(company)
    db.commit()
    return {"success": True, "message": "Empresa excluida com sucesso"}


@router.get("/users")
def listar_usuarios(
    company_id: int | None = None,
    search: str | None = None,
    role: str | None = None,
    ativo: bool | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
):
    target_company_id = resolve_company_id(current_user, company_id)
    query = db.query(User).filter(User.company_id == target_company_id)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(or_(User.email.ilike(term), User.nome.ilike(term)))
    if role:
        query = query.filter(User.role == role)
    if ativo is not None:
        query = query.filter(User.ativo == ativo)
    total = query.count()
    usuarios = query.order_by(User.nome.asc(), User.email.asc()).offset((page - 1) * limit).limit(limit).all()
    metrics_query = db.query(User).filter(User.company_id == target_company_id)
    all_users = metrics_query.all()
    metrics = {
        "total": len(all_users),
        "ativos": sum(1 for user in all_users if user.ativo),
        "inativos": sum(1 for user in all_users if not user.ativo),
        "administradores": sum(1 for user in all_users if user.role == ROLE_ADMIN and user.ativo),
    }
    return {"success": True, "data": [serialize_user(user) for user in usuarios], "total": total, "page": page, "limit": limit, "metrics": metrics}


@router.post("/users")
def criar_usuario(
    body: ManagedUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
):
    target_company_id = resolve_company_id(current_user, body.company_id)
    if body.role == ROLE_MASTER:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Use o bootstrap seguro para Master")

    company = db.query(Company).filter(Company.id == target_company_id, Company.ativo == True).first()
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa nao encontrada")

    # tenant-scope: global - email e unico em todo o sistema.
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ja cadastrado")

    user = User(
        nome=body.nome,
        email=body.email,
        senha_hash=AuthService.hash_password(body.senha),
        company_id=target_company_id,
        role=body.role,
        ativo=True,
        exigir_troca_senha=body.exigir_troca_senha,
    )
    db.add(user)
    db.flush()
    audit_user(db, user, current_user, "criacao", "Usuario criado", {"role": body.role})
    db.commit()
    db.refresh(user)
    return {"success": True, "data": serialize_user(user)}


@router.put("/users/{user_id}")
def atualizar_usuario(
    user_id: int,
    body: ManagedUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
):
    # tenant-scope: global - master pode gerir empresas; autorizacao ocorre abaixo.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

    if not is_master(current_user) and user.company_id != current_user.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    if user.role == ROLE_MASTER and current_user.id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Master nao pode ser alterado aqui")

    if body.role is not None:
        if body.role == ROLE_MASTER:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Perfil Master nao pode ser atribuido aqui")
        if user.role == ROLE_ADMIN and body.role != ROLE_ADMIN:
            ensure_company_has_another_admin(db, user)
        user.role = body.role

    if body.ativo is not None:
        if user.id == current_user.id and body.ativo is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voce nao pode desativar seu proprio usuario")
        if body.ativo is False:
            ensure_company_has_another_admin(db, user)
        user.ativo = body.ativo

    if body.nome is not None:
        user.nome = body.nome

    if body.senha:
        user.senha_hash = AuthService.hash_password(body.senha)
        user.exigir_troca_senha = True

    if body.exigir_troca_senha is not None:
        user.exigir_troca_senha = body.exigir_troca_senha

    audit_user(db, user, current_user, "atualizacao", body.motivo, {
        "role": user.role,
        "ativo": user.ativo,
        "senha_redefinida": bool(body.senha),
    })

    db.commit()
    db.refresh(user)
    return {"success": True, "data": serialize_user(user)}


@router.delete("/users/{user_id}")
def excluir_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
):
    # tenant-scope: global - master pode gerir empresas; autorizacao ocorre abaixo.
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

    if not is_master(current_user) and user.company_id != current_user.company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")

    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Voce nao pode excluir seu proprio usuario")

    if user.role == ROLE_MASTER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Master nao pode ser excluido aqui")

    ensure_company_has_another_admin(db, user)
    user.ativo = False
    audit_user(db, user, current_user, "desativacao", "Desativacao administrativa")
    db.commit()
    db.refresh(user)
    return {"success": True, "message": "Usuario excluido com sucesso", "data": serialize_user(user)}


@router.get("/users/audit/history")
def listar_historico_usuarios(
    company_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
):
    target_company_id = resolve_company_id(current_user, company_id)
    rows = (
        db.query(UserAudit)
        .filter(UserAudit.company_id == target_company_id)
        .order_by(UserAudit.created_at.desc())
        .limit(100)
        .all()
    )
    return {"success": True, "data": [{
        "id": row.id,
        "target_user_id": row.target_user_id,
        "actor_user_id": row.actor_user_id,
        "acao": row.acao,
        "motivo": row.motivo,
        "detalhes": row.detalhes,
        "created_at": row.created_at,
    } for row in rows]}


@router.get("/me")
def obter_me(current_user: User = Depends(get_current_user)):
    return {"success": True, "data": serialize_user(current_user)}
