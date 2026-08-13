from sqlalchemy.orm import Session
from app.models import Customer, PointsTransaction, Product
from typing import Tuple
from decimal import Decimal

class PointsService:
    """
    Serviço de Gestão de Pontos
    
    REGRA CRÍTICA: NUNCA atualizar saldo diretamente
    SEMPRE usar movimentar_pontos()
    """
    
    @staticmethod
    def movimentar_pontos(
        db: Session,
        customer_id: int,
        company_id: int,
        pontos: float,
        tipo: str,
        descricao: str,
        product_id: int = None
    ) -> Tuple[PointsTransaction, Customer]:
        """
        Função central de movimentação de pontos
        
        Args:
            db: Sessão do banco
            customer_id: ID do cliente
            company_id: ID da empresa
            pontos: Quantidade de pontos
            tipo: "entrada" ou "saida"
            descricao: Descrição da transação
        
        Returns:
            Tupla (transação criada, cliente atualizado)
        
        Validações:
            - Previne saldo negativo
            - Registra transação
            - Atualiza saldo do cliente
        """
        
        # Busca cliente
        customer = db.query(Customer).filter(
            Customer.id == customer_id,
            Customer.company_id == company_id
        ).first()
        
        if not customer:
            raise ValueError("Cliente não encontrado")
        
        pontos_decimal = Decimal(str(pontos))

        # Valida pontos
        if pontos_decimal <= 0:
            raise ValueError("Pontos deve ser maior que zero")
        
        # Valida tipo
        if tipo not in ["entrada", "saida"]:
            raise ValueError("Tipo deve ser 'entrada' ou 'saida'")
        
        # Calcula novo saldo
        if tipo == "entrada":
            novo_saldo = customer.pontos + pontos_decimal
        else:  # saida
            novo_saldo = customer.pontos - pontos_decimal
        
        # Previne saldo negativo
        if novo_saldo < 0:
            raise ValueError(f"Saldo insuficiente. Saldo atual: {customer.pontos}")
        
        # Registra transação
        product = None
        if product_id is not None:
            product = db.query(Product).filter(
                Product.id == product_id,
                Product.company_id == company_id
            ).first()
            if not product:
                raise ValueError("Produto nao encontrado")

        transaction = PointsTransaction(
            customer_id=customer_id,
            company_id=company_id,
            product_id=product.id if product else None,
            product_nome=product.nome if product else None,
            pontos=pontos_decimal,
            tipo=tipo,
            descricao=descricao
        )
        db.add(transaction)
        
        # Atualiza saldo do cliente
        customer.pontos = novo_saldo
        db.add(customer)
        
        # Commit atômico
        db.commit()
        db.refresh(transaction)
        db.refresh(customer)
        
        return transaction, customer
    
    @staticmethod
    def get_customer_transactions(
        db: Session,
        customer_id: int,
        company_id: int,
        page: int = 1,
        limit: int = 50
    ) -> Tuple[list, int]:
        """Busca histórico de transações do cliente"""
        
        query = db.query(PointsTransaction).filter(
            PointsTransaction.customer_id == customer_id,
            PointsTransaction.company_id == company_id
        ).order_by(PointsTransaction.created_at.desc())
        
        total = query.count()
        
        transactions = query.offset((page - 1) * limit).limit(limit).all()
        
        return transactions, total
