from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import cast, extract, func, Integer, or_
from sqlalchemy.orm import Session

from app.models import Customer, PointsTransaction, PromotionConfig


class DashboardService:
    """Servico de Dashboard e Relatorios"""

    @staticmethod
    def _number(value) -> float:
        return float(value or 0)

    @staticmethod
    def get_management_analytics(db: Session, company_id: int, days: int = 30) -> dict:
        """Indicadores acionaveis do periodo e comparacao com o periodo anterior."""
        end = datetime.utcnow()
        start = end - timedelta(days=days)
        previous_start = start - timedelta(days=days)

        def period_metrics(period_start: datetime, period_end: datetime) -> dict:
            base = db.query(PointsTransaction).filter(
                PointsTransaction.company_id == company_id,
                PointsTransaction.created_at >= period_start,
                PointsTransaction.created_at < period_end,
            )
            entries = base.filter(PointsTransaction.tipo == "entrada")
            exits = base.filter(PointsTransaction.tipo == "saida")
            active = entries.with_entities(PointsTransaction.customer_id).distinct().count()
            returning = db.query(PointsTransaction.customer_id).filter(
                PointsTransaction.company_id == company_id,
                PointsTransaction.tipo == "entrada",
                PointsTransaction.created_at >= period_start,
                PointsTransaction.created_at < period_end,
            ).group_by(PointsTransaction.customer_id).having(func.count(PointsTransaction.id) >= 2).count()
            purchases = entries.count()
            revenue = entries.with_entities(func.sum(PointsTransaction.valor_compra)).scalar() or 0
            distributed = entries.with_entities(func.sum(PointsTransaction.pontos)).scalar() or 0
            redeemed = exits.with_entities(func.sum(PointsTransaction.pontos)).scalar() or 0
            new_customers = db.query(func.count(Customer.id)).filter(
                Customer.company_id == company_id,
                Customer.created_at >= period_start,
                Customer.created_at < period_end,
            ).scalar() or 0
            return {
                "clientes_ativos": active,
                "clientes_recorrentes": returning,
                "taxa_retorno": round((returning / active * 100) if active else 0, 2),
                "novos_clientes": new_customers,
                "movimentacoes": base.count(),
                "compras": purchases,
                "faturamento_registrado": DashboardService._number(revenue),
                "ticket_medio": round(DashboardService._number(revenue) / purchases, 2) if purchases else 0,
                "pontos_distribuidos": DashboardService._number(distributed),
                "pontos_resgatados": DashboardService._number(redeemed),
                "taxa_resgate": round((DashboardService._number(redeemed) / DashboardService._number(distributed) * 100) if distributed else 0, 2),
            }

        current = period_metrics(start, end)
        previous = period_metrics(previous_start, start)

        def variation(current_value: float, previous_value: float) -> float | None:
            if not previous_value:
                return None if not current_value else 100.0
            return round(((current_value - previous_value) / previous_value) * 100, 2)

        comparison = {key: variation(current[key], previous[key]) for key in current}
        transactions = db.query(PointsTransaction).filter(
            PointsTransaction.company_id == company_id,
            PointsTransaction.created_at >= start,
            PointsTransaction.created_at < end,
        ).order_by(PointsTransaction.created_at.asc()).all()
        daily = {}
        for transaction in transactions:
            key = transaction.created_at.date().isoformat()
            item = daily.setdefault(key, {"data": key, "distribuidos": 0.0, "resgatados": 0.0, "faturamento": 0.0})
            if transaction.tipo == "entrada":
                item["distribuidos"] += DashboardService._number(transaction.pontos)
                item["faturamento"] += DashboardService._number(transaction.valor_compra)
            else:
                item["resgatados"] += DashboardService._number(transaction.pontos)

        inactivity = {
            str(window): len(DashboardService.get_clientes_inativos(db, company_id, window, 10000))
            for window in (15, 30, 60)
        }
        actions = []
        if inactivity["15"]:
            actions.append({"tipo": "reativacao", "prioridade": "alta", "texto": f"Reativar {inactivity['15']} cliente(s) sem compra ha 15 dias."})
        if current["taxa_resgate"] < 10 and current["pontos_distribuidos"] > 0:
            actions.append({"tipo": "resgate", "prioridade": "media", "texto": "Estimular resgates: menos de 10% dos pontos do periodo foram resgatados."})
        if current["novos_clientes"] == 0:
            actions.append({"tipo": "captacao", "prioridade": "media", "texto": "Nenhum cliente novo no periodo; revisar campanha de captacao."})

        return {
            "periodo_dias": days,
            "atual": current,
            "anterior": previous,
            "variacao_percentual": comparison,
            "inativos": inactivity,
            "serie_diaria": list(daily.values()),
            "acoes_recomendadas": actions,
            "observacao_financeira": "Metricas financeiras consideram apenas compras com valor informado.",
        }

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
        pontos = DashboardService._number(customer.pontos)
        percentual = round((pontos / target) * 100, 2) if target > 0 else 0

        return {
            "id": customer.id,
            "nome": customer.nome,
            "telefone": customer.telefone,
            "email": customer.email,
            "pontos": pontos,
            "meta_pontos": target,
            "percentual": percentual,
            "falta": max(round(target - pontos, 2), 0),
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
            if DashboardService._number(cliente.pontos) >= DashboardService._get_customer_points_target(cliente, max_pontos)
        )

        def contar_clientes_inativos(dias: int) -> int:
            data_limite = datetime.utcnow() - timedelta(days=dias)
            return db.query(func.count(Customer.id)).filter(
                Customer.company_id == company_id,
                Customer.ativo == True,
                ~Customer.id.in_(
                    db.query(PointsTransaction.customer_id).filter(
                        PointsTransaction.company_id == company_id,
                        PointsTransaction.created_at >= data_limite
                    )
                )
            ).scalar() or 0

        clientes_inativos_15 = contar_clientes_inativos(15)
        clientes_inativos_30 = contar_clientes_inativos(30)

        mes_atual = datetime.now().month

        if db.bind.dialect.name == "postgresql":
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
            "clientes_inativos": clientes_inativos_15,
            "clientes_inativos_15": clientes_inativos_15,
            "clientes_inativos_30": clientes_inativos_30,
            "aniversariantes_mes": aniversariantes,
            "total_points_distributed": DashboardService._number(total_points_distributed),
            "total_points_redeemed": DashboardService._number(total_points_redeemed),
            "total_points_circulation": DashboardService._number(total_points_circulation),
            "pontos_alvo": max_pontos,
            "percentual_premiacao": 80
        }

    @staticmethod
    def get_clientes_inativos(db: Session, company_id: int, dias: int = 15, limit: int = 50) -> list:
        """Retorna clientes que nao compram ha X dias"""

        try:
            data_limite = datetime.utcnow() - timedelta(days=dias)

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
                    "pontos": DashboardService._number(c.pontos),
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

        if db.bind.dialect.name == "postgresql":
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
                "pontos": DashboardService._number(c.pontos),
                "idade": datetime.now().year - c.data_nascimento.year if c.data_nascimento else None
            }
            for c in aniversariantes
        ]

    @staticmethod
    def get_aniversariantes_dia(db: Session, company_id: int, limit: int = 50) -> list:
        """Retorna clientes aniversariantes de hoje."""

        hoje = datetime.now()

        if db.bind.dialect.name == "postgresql":
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
                "pontos": DashboardService._number(c.pontos),
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
            pontos = DashboardService._number(cliente.pontos)
            percentual = (pontos / target) * 100 if target > 0 else 0

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
                "pontos": DashboardService._number(c.pontos),
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
                "pontos": DashboardService._number(row.pontos),
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
                "pontos": DashboardService._number(t.pontos),
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
            pontos = DashboardService._number(cliente.pontos)
            percentual = (pontos / target) * 100 if target > 0 else 0

            if percentual_min <= percentual < percentual_max:
                quase_premiados.append(DashboardService._build_customer_reward_data(cliente, target))

            if len(quase_premiados) >= limit:
                break

        return quase_premiados

    @staticmethod
    def get_resgates_premios(db: Session, company_id: int, limit: int = 50) -> list:
        """Retorna o historico de premios resgatados pela empresa."""
        rows = (
            db.query(PointsTransaction, Customer)
            .join(Customer, Customer.id == PointsTransaction.customer_id)
            .filter(
                PointsTransaction.company_id == company_id,
                PointsTransaction.tipo == "saida",
                or_(
                    PointsTransaction.descricao.ilike("%resgate%premio%"),
                    PointsTransaction.motivo.ilike("%premio%resgat%"),
                ),
            )
            .order_by(PointsTransaction.created_at.desc())
            .limit(limit)
            .all()
        )
        result = []
        for transaction, customer in rows:
            description = (transaction.descricao or "").strip()
            prize = description.split(":", 1)[1].strip() if ":" in description else ""
            result.append({
                "id": transaction.id,
                "customer_id": customer.id,
                "cliente": customer.nome,
                "telefone": customer.telefone,
                "premio": prize or transaction.product_nome or "Premio nao informado",
                "pontos_resgatados": DashboardService._number(transaction.pontos),
                "data_resgate": transaction.created_at,
            })
        return result

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
            pontos = DashboardService._number(c.pontos)
            percentual = (pontos / target) * 100 if target > 0 else 0

            if percentual >= 100:
                clientes_premiados.append({
                    "id": c.id,
                    "nome": c.nome,
                    "telefone": c.telefone,
                    "email": c.email,
                    "data_nascimento": str(c.data_nascimento) if c.data_nascimento else None,
                    "pontos": pontos,
                    "meta_pontos": target,
                    "percentual": round(percentual, 2),
                    "falta": 0,
                    "valor_gasto_atual": DashboardService._number(c.valor_gasto_atual),
                    "quantidade_produtos_comprados": c.quantidade_produtos_comprados,
                    "created_at": c.created_at
                })

            if len(clientes_premiados) >= limit:
                break

        return clientes_premiados
