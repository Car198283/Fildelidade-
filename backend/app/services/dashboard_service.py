from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import cast, extract, func, Integer
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Customer, PointsTransaction, PromotionConfig


class DashboardService:
    """Servico de Dashboard e Relatorios"""

    @staticmethod
    def _get_default_points_target(db: Session, company_id: int) -> float:
        promocoes = db.query(PromotionConfig).filter(
            PromotionConfig.company_id == company_id,
            PromotionConfig.ativo == True
        ).order_by(PromotionConfig.id.desc()).all()

        for promocao in promocoes:
            tipo = promocao.tipo.value if hasattr(promocao.tipo, "value") else promocao.tipo
            tipo = str(tipo).lower()

            if tipo == "quantidade" and promocao.quantidade_produtos:
                return float(promocao.quantidade_produtos)

            if tipo == "valor" and promocao.valor_gasto:
                return float(promocao.valor_gasto)

        return 100.0

    @staticmethod
    def _get_customer_points_target(customer: Customer, default_target: float) -> float:
        if customer.meta_premiacao_quantidade and customer.meta_premiacao_quantidade > 0:
            return float(customer.meta_premiacao_quantidade)

        if customer.meta_premiacao_valor and customer.meta_premiacao_valor > 0:
            return float(customer.meta_premiacao_valor)

        return default_target

    @staticmethod
    def _build_customer_reward_data(customer: Customer, target: float) -> dict:
        percentual = round((customer.pontos / target) * 100, 2) if target > 0 else 0

        return {
            "id": customer.id,
            "nome": customer.nome,
            "telefone": customer.telefone,
            "email": customer.email,
            "pontos": customer.pontos,
            "meta_pontos": target,
            "percentual": percentual,
            "falta": max(round(target - customer.pontos, 2), 0),
            "created_at": customer.created_at
        }

    @staticmethod
    def get_dashboard_stats(db: Session, company_id: int) -> dict:
        """Retorna estatisticas da empresa"""

        total_customers = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.ativo == True
        ).scalar() or 0

        max_pontos = DashboardService._get_default_points_target(db, company_id)
        clientes_ativos = db.query(Customer).filter(
            Customer.company_id == company_id,
            Customer.ativo == True
        ).all()
        clientes_premiados = sum(
            1
            for cliente in clientes_ativos
            if cliente.pontos >= DashboardService._get_customer_points_target(cliente, max_pontos)
        )

        data_limite = datetime.now() - timedelta(days=15)
        clientes_inativos = db.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.ativo == True,
            ~Customer.id.in_(
                db.query(PointsTransaction.customer_id).filter(
                    PointsTransaction.company_id == company_id,
                    PointsTransaction.created_at >= data_limite
                )
            )
        ).scalar() or 0

        mes_atual = datetime.now().month

        if settings.db_type.lower() == "postgresql":
            aniversariantes = db.query(func.count(Customer.id)).filter(
                Customer.company_id == company_id,
                Customer.ativo == True,
                extract("month", Customer.data_nascimento) == mes_atual,
                Customer.data_nascimento != None
            ).scalar() or 0
        else:
            aniversariantes = db.query(func.count(Customer.id)).filter(
                Customer.company_id == company_id,
                Customer.ativo == True,
                cast(func.strftime("%m", Customer.data_nascimento), Integer) == mes_atual,
                Customer.data_nascimento != None
            ).scalar() or 0

        total_points_distributed = db.query(func.sum(PointsTransaction.pontos)).filter(
            PointsTransaction.company_id == company_id,
            PointsTransaction.tipo == "entrada"
        ).scalar() or 0

        total_points_redeemed = db.query(func.sum(PointsTransaction.pontos)).filter(
            PointsTransaction.company_id == company_id,
            PointsTransaction.tipo == "saida"
        ).scalar() or 0

        total_points_circulation = db.query(func.sum(Customer.pontos)).filter(
            Customer.company_id == company_id,
            Customer.ativo == True
        ).scalar() or 0

        return {
            "total_clientes": total_customers,
            "clientes_premiados": clientes_premiados,
            "clientes_inativos": clientes_inativos,
            "aniversariantes_mes": aniversariantes,
            "total_points_distributed": total_points_distributed or 0,
            "total_points_redeemed": total_points_redeemed or 0,
            "total_points_circulation": total_points_circulation or 0,
            "pontos_alvo": max_pontos,
            "percentual_premiacao": 80
        }

    @staticmethod
    def get_clientes_inativos(db: Session, company_id: int, dias: int = 15, limit: int = 50) -> list:
        """Retorna clientes que nao compram ha X dias"""

        try:
            data_limite = datetime.now() - timedelta(days=dias)

            clientes_inativos = db.query(Customer).filter(
                Customer.company_id == company_id,
                Customer.ativo == True,
                ~Customer.id.in_(
                    db.query(PointsTransaction.customer_id).filter(
                        PointsTransaction.company_id == company_id,
                        PointsTransaction.created_at >= data_limite
                    )
                )
            ).limit(limit).all()

            return [
                {
                    "id": c.id,
                    "nome": c.nome,
                    "telefone": c.telefone,
                    "email": c.email,
                    "pontos": c.pontos,
                    "created_at": c.created_at
                }
                for c in clientes_inativos
            ]
        except Exception:
            return []

    @staticmethod
    def get_aniversariantes(db: Session, company_id: int, mes: Optional[int] = None, limit: int = 50) -> list:
        """Retorna clientes aniversariantes do mes"""

        if mes is None:
            mes = datetime.now().month

        if settings.db_type.lower() == "postgresql":
            month_filter = extract("month", Customer.data_nascimento) == mes
            day_order = extract("day", Customer.data_nascimento)
        else:
            month_filter = cast(func.strftime("%m", Customer.data_nascimento), Integer) == mes
            day_order = cast(func.strftime("%d", Customer.data_nascimento), Integer)

        aniversariantes = db.query(Customer).filter(
            Customer.company_id == company_id,
            Customer.ativo == True,
            month_filter,
            Customer.data_nascimento != None
        ).order_by(day_order).limit(limit).all()

        return [
            {
                "id": c.id,
                "nome": c.nome,
                "telefone": c.telefone,
                "email": c.email,
                "data_nascimento": str(c.data_nascimento),
                "pontos": c.pontos,
                "idade": datetime.now().year - c.data_nascimento.year if c.data_nascimento else None
            }
            for c in aniversariantes
        ]

    @staticmethod
    def get_aniversariantes_dia(db: Session, company_id: int, limit: int = 50) -> list:
        """Retorna clientes aniversariantes de hoje."""

        hoje = datetime.now()

        if settings.db_type.lower() == "postgresql":
            month_filter = extract("month", Customer.data_nascimento) == hoje.month
            day_filter = extract("day", Customer.data_nascimento) == hoje.day
        else:
            month_filter = cast(func.strftime("%m", Customer.data_nascimento), Integer) == hoje.month
            day_filter = cast(func.strftime("%d", Customer.data_nascimento), Integer) == hoje.day

        aniversariantes = db.query(Customer).filter(
            Customer.company_id == company_id,
            Customer.ativo == True,
            month_filter,
            day_filter,
            Customer.data_nascimento != None
        ).order_by(Customer.nome.asc()).limit(limit).all()

        return [
            {
                "id": c.id,
                "nome": c.nome,
                "telefone": c.telefone,
                "email": c.email,
                "data_nascimento": str(c.data_nascimento),
                "pontos": c.pontos,
                "idade": datetime.now().year - c.data_nascimento.year if c.data_nascimento else None
            }
            for c in aniversariantes
        ]

    @staticmethod
    def get_clientes_premiados(db: Session, company_id: int, min_percentual: float = 80, limit: int = 50) -> list:
        """Retorna clientes que atingiram percentual minimo de pontos"""

        default_target = DashboardService._get_default_points_target(db, company_id)
        clientes = db.query(Customer).filter(
            Customer.company_id == company_id,
            Customer.ativo == True
        ).order_by(Customer.pontos.desc()).all()

        premiados = []
        for cliente in clientes:
            target = DashboardService._get_customer_points_target(cliente, default_target)
            percentual = (cliente.pontos / target) * 100 if target > 0 else 0

            if percentual >= min_percentual:
                premiados.append(DashboardService._build_customer_reward_data(cliente, target))

            if len(premiados) >= limit:
                break

        return premiados

    @staticmethod
    def get_top_customers(db: Session, company_id: int, limit: int = 10) -> list:
        """Retorna top clientes com mais pontos"""

        top_clientes = db.query(Customer).filter(
            Customer.company_id == company_id,
            Customer.ativo == True
        ).order_by(Customer.pontos.desc()).limit(limit).all()

        return [
            {
                "id": c.id,
                "nome": c.nome,
                "telefone": c.telefone,
                "email": c.email,
                "pontos": c.pontos,
                "created_at": c.created_at
            }
            for c in top_clientes
        ]

    @staticmethod
    def get_produtos_mais_vendidos(db: Session, company_id: int, limit: int = 10) -> list:
        """Retorna produtos mais consumidos nos lancamentos de pontos."""

        rows = db.query(
            PointsTransaction.product_id,
            PointsTransaction.product_nome,
            func.count(PointsTransaction.id).label("quantidade"),
            func.sum(PointsTransaction.pontos).label("pontos")
        ).filter(
            PointsTransaction.company_id == company_id,
            PointsTransaction.tipo == "entrada",
            PointsTransaction.product_nome != None
        ).group_by(
            PointsTransaction.product_id,
            PointsTransaction.product_nome
        ).order_by(
            func.count(PointsTransaction.id).desc()
        ).limit(limit).all()

        return [
            {
                "product_id": row.product_id,
                "produto": row.product_nome,
                "quantidade": row.quantidade,
                "pontos": row.pontos or 0
            }
            for row in rows
        ]

    @staticmethod
    def get_produtos_consumidos_cliente(db: Session, company_id: int, customer_id: int, limit: int = 50) -> list:
        """Retorna historico de produtos consumidos por um cliente."""

        transacoes = db.query(PointsTransaction).filter(
            PointsTransaction.company_id == company_id,
            PointsTransaction.customer_id == customer_id,
            PointsTransaction.tipo == "entrada",
            PointsTransaction.product_nome != None
        ).order_by(PointsTransaction.created_at.desc()).limit(limit).all()

        return [
            {
                "id": t.id,
                "product_id": t.product_id,
                "produto": t.product_nome,
                "pontos": t.pontos,
                "descricao": t.descricao,
                "created_at": t.created_at
            }
            for t in transacoes
        ]

    @staticmethod
    def get_clientes_quase_premiados(
        db: Session,
        company_id: int,
        percentual_min: float = 80,
        percentual_max: float = 99.9,
        limit: int = 50
    ) -> list:
        """Retorna clientes que estao entre 80% e 99.9% da meta."""

        default_target = DashboardService._get_default_points_target(db, company_id)
        clientes = db.query(Customer).filter(
            Customer.company_id == company_id,
            Customer.ativo == True
        ).order_by(Customer.pontos.desc()).all()

        quase_premiados = []
        for cliente in clientes:
            target = DashboardService._get_customer_points_target(cliente, default_target)
            percentual = (cliente.pontos / target) * 100 if target > 0 else 0

            if percentual_min <= percentual < percentual_max:
                quase_premiados.append(DashboardService._build_customer_reward_data(cliente, target))

            if len(quase_premiados) >= limit:
                break

        return quase_premiados

    @staticmethod
    def get_clientes_premiados_completo(db: Session, company_id: int, limit: int = 50) -> list:
        """Retorna clientes 100% premiados com informacoes completas"""

        default_target = DashboardService._get_default_points_target(db, company_id)
        clientes = db.query(Customer).filter(
            Customer.company_id == company_id,
            Customer.ativo == True
        ).order_by(Customer.pontos.desc()).all()

        clientes_premiados = []
        for c in clientes:
            target = DashboardService._get_customer_points_target(c, default_target)
            percentual = (c.pontos / target) * 100 if target > 0 else 0

            if percentual >= 100:
                clientes_premiados.append({
                    "id": c.id,
                    "nome": c.nome,
                    "telefone": c.telefone,
                    "email": c.email,
                    "data_nascimento": str(c.data_nascimento) if c.data_nascimento else None,
                    "pontos": c.pontos,
                    "meta_pontos": target,
                    "percentual": round(percentual, 2),
                    "falta": 0,
                    "valor_gasto_atual": c.valor_gasto_atual,
                    "quantidade_produtos_comprados": c.quantidade_produtos_comprados,
                    "created_at": c.created_at
                })

            if len(clientes_premiados) >= limit:
                break

        return clientes_premiados
