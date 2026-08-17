import os
import tempfile
import unittest
from pathlib import Path

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(tempfile.gettempdir()) / "fidelidade_points_test.db")
os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"

from app.database import SessionLocal, engine
from app.models import Base, Company, Customer, User
from app.services.points_service import PointsService
from app.services.dashboard_service import DashboardService


class PointsIntegrityTestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        self.db = SessionLocal()
        company = Company(nome="Empresa", ativo=True)
        self.db.add(company)
        self.db.flush()
        user = User(email="admin@teste.local", senha_hash="x", company_id=company.id, role="admin", ativo=True)
        customer = Customer(nome="Cliente", telefone="1", company_id=company.id, pontos=0)
        self.db.add_all([user, customer])
        self.db.commit()
        self.company_id, self.user_id, self.customer_id = company.id, user.id, customer.id

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(engine)

    def test_repeticao_da_chave_nao_duplica_lancamento(self):
        args = dict(
            db=self.db, customer_id=self.customer_id, company_id=self.company_id,
            pontos=10, tipo="entrada", descricao="Compra", user_id=self.user_id,
            origem="test", motivo="Compra identificada", idempotency_key="pedido-12345",
        )
        first, customer = PointsService.movimentar_pontos(**args)
        second, customer = PointsService.movimentar_pontos(**args)
        self.assertEqual(first.id, second.id)
        self.assertEqual(float(customer.pontos), 10.0)

    def test_cliente_de_outra_empresa_nao_e_alterado(self):
        other = Company(nome="Outra", ativo=True)
        self.db.add(other)
        self.db.commit()
        with self.assertRaisesRegex(ValueError, "Cliente"):
            PointsService.movimentar_pontos(
                self.db, self.customer_id, other.id, 10, "entrada", "Compra",
                user_id=self.user_id, origem="test", motivo="Teste", idempotency_key="pedido-99999",
            )

    def test_dashboard_expoe_inativos_de_15_e_30_dias(self):
        stats = DashboardService.get_dashboard_stats(self.db, self.company_id)
        self.assertEqual(stats["total_clientes"], 1)
        self.assertEqual(stats["clientes_inativos_15"], 1)
        self.assertEqual(stats["clientes_inativos_30"], 1)
        self.assertIn("total_points_circulation", stats)


if __name__ == "__main__":
    unittest.main()
