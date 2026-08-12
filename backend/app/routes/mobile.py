from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Customer, User, PointsTransaction
from app.schemas.schemas import CustomerCreate, PointsTransactionCreate
from app.utils.dependencies import get_current_user, get_writable_company_id
from datetime import datetime

router = APIRouter(prefix="/mobile", tags=["Mobile"])

@router.post("/cliente/registrar")
def registrar_cliente_mobile(
    nome: str = Query(..., min_length=1, max_length=255),
    telefone: str = Query(..., min_length=8, max_length=20),
    email: str = Query(None),
    data_nascimento: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_writable_company_id)
):
    """
    Registra novo cliente via mobile (simplificado)
    - corpo da requisição via query params
    - retorna ID do cliente criado
    """
    
    # Verifica se telefone já existe
    cliente_existente = db.query(Customer).filter(
        Customer.telefone == telefone,
        Customer.company_id == company_id
    ).first()
    
    if cliente_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cliente com telefone {telefone} já existe"
        )
    
    # Parse data_nascimento
    data_nasc = None
    if data_nascimento:
        try:
            # Esperado formato: DD/MM/YYYY ou YYYY-MM-DD
            if "/" in data_nascimento:
                data_nasc = datetime.strptime(data_nascimento, "%d/%m/%Y").date()
            else:
                data_nasc = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de nascimento inválida. Use formato DD/MM/YYYY ou YYYY-MM-DD"
            )
    
    # Cria cliente
    cliente = Customer(
        nome=nome,
        telefone=telefone,
        email=email,
        data_nascimento=data_nasc,
        company_id=company_id,
        pontos=0.0,
        ativo=True
    )
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    
    return {
        "success": True,
        "message": f"Cliente '{nome}' registrado com sucesso",
        "data": {
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone,
            "email": cliente.email,
            "data_nascimento": str(cliente.data_nascimento) if cliente.data_nascimento else None,
            "pontos": cliente.pontos,
            "created_at": cliente.created_at.isoformat()
        }
    }

@router.get("/cliente/buscar-por-telefone")
def buscar_cliente_por_telefone(
    telefone: str = Query(..., min_length=8, max_length=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca cliente por telefone (sem autenticação se necessário)
    Retorna dados do cliente e saldo de pontos
    """
    
    cliente = db.query(Customer).filter(
        Customer.telefone == telefone,
        Customer.company_id == current_user.company_id,
        Customer.ativo == True
    ).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com telefone {telefone} não encontrado"
        )
    
    # Últimas 5 transações
    transacoes = db.query(PointsTransaction).filter(
        PointsTransaction.customer_id == cliente.id
    ).order_by(PointsTransaction.created_at.desc()).limit(5).all()
    
    return {
        "success": True,
        "data": {
            "id": cliente.id,
            "nome": cliente.nome,
            "telefone": cliente.telefone,
            "email": cliente.email,
            "data_nascimento": str(cliente.data_nascimento) if cliente.data_nascimento else None,
            "pontos": cliente.pontos,
            "created_at": cliente.created_at.isoformat(),
            "transacoes_recentes": [
                {
                    "id": t.id,
                    "pontos": t.pontos,
                    "tipo": t.tipo,
                    "descricao": t.descricao,
                    "data": t.created_at.isoformat()
                }
                for t in transacoes
            ]
        }
    }

@router.post("/pontos/lancar-por-telefone")
def lancar_pontos_por_telefone(
    telefone: str = Query(..., min_length=8, max_length=20),
    pontos: float = Query(..., gt=0),
    descricao: str = Query(None, max_length=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_writable_company_id)
):
    """
    Lança pontos para cliente via telefone
    - Busca cliente por telefone
    - Adiciona pontos
    - Registra transação
    """
    
    # Busca cliente
    cliente = db.query(Customer).filter(
        Customer.telefone == telefone,
        Customer.company_id == company_id,
        Customer.ativo == True
    ).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com telefone {telefone} não encontrado"
        )
    
    # Valida pontos
    if pontos <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pontos devem ser maiores que zero"
        )
    
    # Adiciona pontos
    cliente.pontos += pontos
    
    # Cria transação
    transacao = PointsTransaction(
        customer_id=cliente.id,
        company_id=company_id,
        pontos=pontos,
        tipo="entrada",
        descricao=descricao or f"Lançamento manual via mobile"
    )
    db.add(transacao)
    db.commit()
    db.refresh(cliente)
    db.refresh(transacao)
    
    return {
        "success": True,
        "message": f"✅ {pontos} ponto(s) adicionado(s) para {cliente.nome}",
        "data": {
            "cliente_id": cliente.id,
            "cliente_nome": cliente.nome,
            "pontos_adicionados": pontos,
            "novo_saldo": cliente.pontos,
            "transacao_id": transacao.id,
            "data": transacao.created_at.isoformat()
        }
    }

@router.post("/pontos/resgatar-por-telefone")
def resgatar_pontos_por_telefone(
    telefone: str = Query(..., min_length=8, max_length=20),
    pontos: float = Query(..., gt=0),
    descricao: str = Query(None, max_length=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company_id: int = Depends(get_writable_company_id)
):
    """
    Resgata (desconta) pontos de cliente via telefone
    - Valida saldo suficiente
    - Desconta pontos
    - Registra transação como saída
    """
    
    # Busca cliente
    cliente = db.query(Customer).filter(
        Customer.telefone == telefone,
        Customer.company_id == company_id,
        Customer.ativo == True
    ).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente com telefone {telefone} não encontrado"
        )
    
    # Valida saldo
    if cliente.pontos < pontos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Saldo insuficiente. Cliente tem {cliente.pontos:.2f} pontos, tentou resgatar {pontos}"
        )
    
    # Desconta pontos
    cliente.pontos -= pontos
    
    # Cria transação
    transacao = PointsTransaction(
        customer_id=cliente.id,
        company_id=company_id,
        pontos=pontos,
        tipo="saida",
        descricao=descricao or "Resgate de pontos via mobile"
    )
    db.add(transacao)
    db.commit()
    db.refresh(cliente)
    db.refresh(transacao)
    
    return {
        "success": True,
        "message": f"✅ {pontos} ponto(s) resgatado(s) por {cliente.nome}",
        "data": {
            "cliente_id": cliente.id,
            "cliente_nome": cliente.nome,
            "pontos_resgatados": pontos,
            "novo_saldo": cliente.pontos,
            "transacao_id": transacao.id,
            "data": transacao.created_at.isoformat()
        }
    }

@router.get("/cliente/listar")
def listar_clientes_mobile(
    search: str = Query(None, min_length=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista clientes (para busca em mobile)
    - Pode filtrar por nome ou telefone
    - Retorna dados simplificados
    """
    
    query = db.query(Customer).filter(
        Customer.company_id == current_user.company_id,
        Customer.ativo == True
    )
    
    # Filtro de busca
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Customer.nome.ilike(search_term)) |
            (Customer.telefone.ilike(search_term))
        )
    
    clientes = query.limit(limit).all()
    
    return {
        "success": True,
        "total": len(clientes),
        "data": [
            {
                "id": c.id,
                "nome": c.nome,
                "telefone": c.telefone,
                "pontos": c.pontos,
                "email": c.email
            }
            for c in clientes
        ]
    }
