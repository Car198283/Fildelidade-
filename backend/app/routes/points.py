from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.schemas import PointsTransactionCreate
from app.services.points_service import PointsService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/clientes", tags=["Points"])

@router.post("/{customer_id}/pontos")
def movimentar_pontos(
    customer_id: int,
    body: PointsTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Movimenta pontos do cliente (entrada ou saida)
    
    FUNÇÃO CRÍTICA: Garante que pontos NUNCA são atualizados diretamente
    """
    
    try:
        transaction, customer = PointsService.movimentar_pontos(
            db=db,
            customer_id=customer_id,
            company_id=current_user.company_id,
            pontos=body.pontos,
            tipo=body.tipo,
            descricao=body.descricao,
            product_id=body.product_id
        )
        
        return {
            "success": True,
            "message": f"Pontos movimentados com sucesso",
            "transaction": {
                "id": transaction.id,
                "pontos": transaction.pontos,
                "tipo": transaction.tipo,
                "descricao": transaction.descricao,
                "product_id": transaction.product_id,
                "product_nome": transaction.product_nome,
                "created_at": transaction.created_at
            },
            "customer": {
                "id": customer.id,
                "nome": customer.nome,
                "pontos": customer.pontos
            }
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao movimentar pontos"
        )

@router.get("/{customer_id}/pontos/historico")
def obter_historico_pontos(
    customer_id: int,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtém histórico de transações do cliente"""
    
    transactions, total = PointsService.get_customer_transactions(
        db=db,
        customer_id=customer_id,
        company_id=current_user.company_id,
        page=page,
        limit=limit
    )
    
    return {
        "success": True,
        "total": total,
        "page": page,
        "limit": limit,
        "data": [
            {
                "id": t.id,
                "pontos": t.pontos,
                "tipo": t.tipo,
                "descricao": t.descricao,
                "product_id": t.product_id,
                "product_nome": t.product_nome,
                "created_at": t.created_at
            }
            for t in transactions
        ]
    }
