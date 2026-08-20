from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, text
from app.database import get_db
from app.models import Company, Customer, PointsTransaction, User
from app.schemas.schemas import CustomerCreate, CustomerUpdate, CustomerResponse, PublicCustomerRegistration
from app.utils.dependencies import (
    get_effective_company_id,
    get_writable_company_id,
    require_admin_or_master,
    require_capture_operator,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/clientes", tags=["Customers"])

@router.post("/", response_model=dict)
def criar_cliente(
    body: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_capture_operator),
    company_id: int = Depends(get_writable_company_id)
):
    """Cria novo cliente"""
    
    cliente = Customer(
        nome=body.nome,
        telefone=body.telefone,
        email=body.email,
        data_nascimento=body.data_nascimento,  # NOVO
        company_id=company_id,
        pontos=0.0,
        ativo=True  # NOVO
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    
    return {
        "success": True,
        "data": {
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone,
            "email": cliente.email,
            "data_nascimento": cliente.data_nascimento,  # NOVO
            "pontos": cliente.pontos,
            "ativo": cliente.ativo,  # NOVO
            "created_at": cliente.created_at
        }
    }

@router.post("/registro-link")
def gerar_link_cadastro(current_user: User = Depends(require_admin_or_master)):
    """Gera um convite seguro para cadastro público de clientes."""
    token = AuthService.create_customer_registration_token(current_user.company_id)
    return {"success": True, "data": {"token": token, "expires_in_days": 30}}

@router.post("/cadastro-publico")
def cadastrar_cliente_publico(
    body: PublicCustomerRegistration,
    db: Session = Depends(get_db)
):
    """Permite o cadastro do cliente por um convite válido."""
    company_id = AuthService.verify_customer_registration_token(body.token)
    if company_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Link de cadastro inválido ou expirado")

    company = db.query(Company).filter(Company.id == company_id).first()
    if not company or not company.ativo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Empresa bloqueada")
    if company.read_only:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Conta em somente leitura")

    cliente = Customer(
        nome=body.nome.strip(),
        telefone=body.telefone,
        email=body.email,
        data_nascimento=body.data_nascimento,
        company_id=company_id,
        pontos=0.0,
        ativo=True
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return {"success": True, "message": "Cadastro realizado com sucesso", "data": {"id": cliente.id, "nome": cliente.nome}}
@router.get("/")
def listar_clientes(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    db: Session = Depends(get_db),
    company_id: int = Depends(get_effective_company_id)
):
    """Lista clientes com filtros e paginação"""
    
    query = db.query(Customer).filter(
        Customer.company_id == company_id,
        Customer.ativo == True  # Apenas clientes ativos
    )
    
    # Filtro de busca por nome, telefone ou email. Para telefone, tambem compara so os numeros.
    if search:
        search_value = search.strip()
        search_term = f"%{search_value}%"
        filters = [
            Customer.nome.ilike(search_term),
            Customer.telefone.ilike(search_term),
            Customer.email.ilike(search_term),
        ]

        digits = "".join(char for char in search_value if char.isdigit())
        if digits:
            phone_digits = func.replace(
                func.replace(
                    func.replace(
                        func.replace(
                            func.replace(Customer.telefone, " ", ""),
                            "-",
                            "",
                        ),
                        "(",
                        "",
                    ),
                    ")",
                    "",
                ),
                "+",
                "",
            )
            filters.append(phone_digits.ilike(f"%{digits}%"))

        query = query.filter(or_(*filters))
    
    total = query.count()
    
    clientes = query.offset((page - 1) * limit).limit(limit).all()
    
    data = [
        {
            "id": c.id,
            "nome": c.nome,
            "telefone": c.telefone,
            "email": c.email,
            "data_nascimento": c.data_nascimento,  # NOVO
            "pontos": c.pontos,
            "ativo": c.ativo,  # NOVO
            "created_at": c.created_at
        }
        for c in clientes
    ]
    
    return {
        "success": True,
        "total": total,
        "page": page,
        "limit": limit,
        "data": data
    }

@router.get("/{cliente_id}")
def obter_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    company_id: int = Depends(get_effective_company_id)
):
    """Obtém detalhes do cliente com histórico de transações"""
    
    cliente = db.query(Customer).filter(
        Customer.id == cliente_id,
        Customer.company_id == company_id,
        Customer.ativo == True  # Apenas clientes ativos
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Histórico de transações
    transactions = db.query(
        PointsTransaction.id,
        PointsTransaction.pontos,
        PointsTransaction.valor_compra,
        PointsTransaction.tipo,
        PointsTransaction.descricao,
        PointsTransaction.motivo,
        PointsTransaction.product_id,
        PointsTransaction.product_nome,
        User.nome.label("usuario_nome"),
        User.email.label("usuario_email"),
        PointsTransaction.created_at
    ).outerjoin(User, User.id == PointsTransaction.user_id).filter(
        PointsTransaction.customer_id == cliente_id,
        PointsTransaction.company_id == company_id
    ).order_by(PointsTransaction.created_at.desc()).limit(100).all()

    purchase_filter = (
        PointsTransaction.customer_id == cliente_id,
        PointsTransaction.company_id == company_id,
        PointsTransaction.tipo == "entrada",
        PointsTransaction.valor_compra.isnot(None),
    )
    purchase_summary = db.query(
        func.count(PointsTransaction.id),
        func.coalesce(func.sum(PointsTransaction.valor_compra), 0),
        func.coalesce(func.avg(PointsTransaction.valor_compra), 0),
        func.max(PointsTransaction.created_at),
    ).filter(*purchase_filter).one()
    favorite_product = db.query(
        PointsTransaction.product_nome,
        func.count(PointsTransaction.id).label("total"),
    ).filter(
        *purchase_filter,
        PointsTransaction.product_nome.isnot(None),
    ).group_by(PointsTransaction.product_nome).order_by(
        func.count(PointsTransaction.id).desc(),
        PointsTransaction.product_nome.asc(),
    ).first()
    
    transactions_formatted = [
        {
            "id": t.id,
            "pontos": t.pontos,
            "valor_compra": t.valor_compra,
            "tipo": t.tipo,
            "descricao": t.descricao,
            "motivo": t.motivo,
            "product_id": t.product_id,
            "product_nome": t.product_nome,
            "usuario_nome": t.usuario_nome or t.usuario_email,
            "created_at": t.created_at
        }
        for t in transactions
    ]
    
    return {
        "success": True,
        "data": {
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone,
            "email": cliente.email,
            "data_nascimento": cliente.data_nascimento,  # NOVO
            "pontos": cliente.pontos,
            "ativo": cliente.ativo,  # NOVO
            "created_at": cliente.created_at,
            "transactions": transactions_formatted,
            "purchase_profile": {
                "total_compras": purchase_summary[0],
                "total_gasto": purchase_summary[1],
                "ticket_medio": purchase_summary[2],
                "ultima_compra": purchase_summary[3],
                "produto_favorito": favorite_product[0] if favorite_product else None,
            }
        }
    }

@router.put("/{cliente_id}")
def atualizar_cliente(
    cliente_id: int,
    body: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id)
):
    """Atualiza dados do cliente (não pontos!)"""
    
    cliente = db.query(Customer).filter(
        Customer.id == cliente_id,
        Customer.company_id == company_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Atualiza apenas campos permitidos
    if body.nome is not None:
        cliente.nome = body.nome
    if body.telefone is not None:
        cliente.telefone = body.telefone
    if body.email is not None:
        cliente.email = body.email
    if body.data_nascimento is not None:  # NOVO
        cliente.data_nascimento = body.data_nascimento
    # Campos de premiação
    if body.valor_gasto_atual is not None:
        cliente.valor_gasto_atual = body.valor_gasto_atual
    if body.quantidade_produtos_comprados is not None:
        cliente.quantidade_produtos_comprados = body.quantidade_produtos_comprados
    if body.meta_premiacao_valor is not None:
        cliente.meta_premiacao_valor = body.meta_premiacao_valor
    if body.meta_premiacao_quantidade is not None:
        cliente.meta_premiacao_quantidade = body.meta_premiacao_quantidade
    
    db.commit()
    db.refresh(cliente)
    
    return {
        "success": True,
        "data": {
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone,
            "email": cliente.email,
            "data_nascimento": cliente.data_nascimento,
            "pontos": cliente.pontos,
            "valor_gasto_atual": cliente.valor_gasto_atual,
            "quantidade_produtos_comprados": cliente.quantidade_produtos_comprados,
            "meta_premiacao_valor": cliente.meta_premiacao_valor,
            "meta_premiacao_quantidade": cliente.meta_premiacao_quantidade,
            "ativo": cliente.ativo,
            "created_at": cliente.created_at
        }
    }

@router.delete("/{cliente_id}")
def deletar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_master),
    company_id: int = Depends(get_writable_company_id)
):
    """Deleta (desativa) cliente logicamente"""
    
    cliente = db.query(Customer).filter(
        Customer.id == cliente_id,
        Customer.company_id == company_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Desativa cliente (soft delete)
    cliente.ativo = False
    db.commit()
    
    return {
        "success": True,
        "message": f"Cliente {cliente.nome} foi desativado com sucesso"
    }

@router.get("/{cliente_id}/detalhes")
def obter_detalhes_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    company_id: int = Depends(get_effective_company_id)
):
    """Obtém detalhes completos do cliente para o modal de edição"""
    
    cliente = db.query(Customer).filter(
        Customer.id == cliente_id,
        Customer.company_id == company_id
    ).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return {
        "success": True,
        "data": {
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone,
            "email": cliente.email,
            "data_nascimento": cliente.data_nascimento,
            "pontos": cliente.pontos,
            "valor_gasto_atual": cliente.valor_gasto_atual,
            "quantidade_produtos_comprados": cliente.quantidade_produtos_comprados,
            "meta_premiacao_valor": cliente.meta_premiacao_valor,
            "meta_premiacao_quantidade": cliente.meta_premiacao_quantidade,
            "ativo": cliente.ativo,
            "created_at": cliente.created_at
        }
    }
