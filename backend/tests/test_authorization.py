import os
import tempfile
import unittest
from pathlib import Path

os.environ["DB_TYPE"] = "sqlite"
os.environ["SQLITE_PATH"] = str(Path(tempfile.gettempdir()) / "fidelidade_authorization_test.db")
os.environ["SECRET_KEY"] = "test-secret-key-for-authorization-suite"

from fastapi.testclient import TestClient

from app.database import SessionLocal, engine
from app.main import app
from app.models import Base, Company, Customer, User
from app.services.auth_service import AuthService


class AuthorizationTestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.db = SessionLocal()

        self.company = Company(nome="Empresa A", ativo=True, read_only=False)
        self.other_company = Company(nome="Empresa B", ativo=True, read_only=False)
        self.read_only_company = Company(nome="Empresa C", ativo=True, read_only=True)
        self.blocked_company = Company(nome="Empresa D", ativo=False, read_only=False)
        self.master_company = Company(nome="Master", ativo=True, read_only=False)
        self.db.add_all(
            [
                self.company,
                self.other_company,
                self.read_only_company,
                self.blocked_company,
                self.master_company,
            ]
        )
        self.db.flush()

        self.admin = self._user("admin@example.com", self.company.id, "admin")
        self.observer = self._user("observer@example.com", self.company.id, "observador")
        self.operator = self._user("operator@example.com", self.company.id, "operador_captura")
        self.inactive_user = self._user("inactive@example.com", self.company.id, "admin", ativo=False)
        self.read_only_admin = self._user("readonly@example.com", self.read_only_company.id, "admin")
        self.blocked_admin = self._user("blocked@example.com", self.blocked_company.id, "admin")
        self.master = self._user("master@example.com", self.master_company.id, "master")

        self.customer = Customer(nome="Cliente A", telefone="111", company_id=self.company.id, pontos=10)
        self.other_customer = Customer(nome="Cliente B", telefone="222", company_id=self.other_company.id, pontos=5)
        self.db.add_all([self.customer, self.other_customer])
        self.db.commit()

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    def _user(self, email, company_id, role, ativo=True):
        user = User(
            email=email,
            senha_hash=AuthService.hash_password("1234567890"),
            company_id=company_id,
            role=role,
            ativo=ativo,
        )
        self.db.add(user)
        return user

    def _headers(self, user, company_id=None):
        token = AuthService.create_access_token({"sub": str(user.id), "company_id": user.company_id})
        headers = {"Authorization": f"Bearer {token}"}
        if company_id is not None:
            headers["X-Company-Id"] = str(company_id)
        return headers

    def test_observador_nao_cria_cliente(self):
        response = self.client.post(
            "/clientes/",
            json={"nome": "Novo", "telefone": "333"},
            headers=self._headers(self.observer),
        )
        self.assertEqual(response.status_code, 403)

    def test_observador_nao_movimenta_pontos(self):
        response = self.client.post(
            f"/clientes/{self.customer.id}/pontos",
            json={"pontos": 1, "tipo": "entrada", "descricao": "Teste"},
            headers=self._headers(self.observer),
        )
        self.assertEqual(response.status_code, 403)

    def test_operador_captura_nao_acessa_admin(self):
        response = self.client.get("/admin/users", headers=self._headers(self.operator))
        self.assertEqual(response.status_code, 403)

    def test_admin_nao_acessa_cliente_de_outra_empresa(self):
        response = self.client.get(
            f"/clientes/{self.other_customer.id}",
            headers=self._headers(self.admin, company_id=self.other_company.id),
        )
        self.assertEqual(response.status_code, 404)

    def test_master_seleciona_empresa_ativa(self):
        response = self.client.get(
            "/clientes/",
            headers=self._headers(self.master, company_id=self.other_company.id),
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual([item["id"] for item in data], [self.other_customer.id])

    def test_master_cria_empresa_com_admin(self):
        response = self.client.post(
            "/admin/companies",
            json={
                "razao_social": "Barcellos Gelataria LTDA",
                "nome": "Barcellos Gelataria",
                "cnpj": "12.345.678/0001-90",
                "telefone": "(32) 99999-9999",
                "email": "contato@barcellos.com.br",
                "responsavel": "Carlos Eduardo",
                "cep": "36000-000",
                "endereco": "Rua Exemplo",
                "numero": "100",
                "bairro": "Centro",
                "cidade": "Juiz de Fora",
                "estado": "MG",
                "logotipo": "logo.png",
                "admin_email": "admin-barcellos@example.com",
                "admin_senha": "1234567890",
            },
            headers=self._headers(self.master),
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()["data"]
        self.assertEqual(data["company"]["razao_social"], "Barcellos Gelataria LTDA")
        self.assertEqual(data["company"]["cnpj"], "12.345.678/0001-90")
        self.assertEqual(data["admin"]["role"], "admin")

    def test_master_nao_cria_empresa_com_cnpj_duplicado(self):
        self.company.cnpj = "12.345.678/0001-90"
        self.db.commit()

        response = self.client.post(
            "/admin/companies",
            json={
                "razao_social": "Outra Empresa LTDA",
                "nome": "Outra Empresa",
                "cnpj": "12.345.678/0001-90",
                "telefone": "(32) 99999-9999",
                "email": "contato-outra@example.com",
                "responsavel": "Maria Silva",
                "admin_email": "admin-outra@example.com",
                "admin_senha": "1234567890",
            },
            headers=self._headers(self.master),
        )
        self.assertEqual(response.status_code, 400)

    def test_usuario_bloqueado_nao_usa_token_antigo(self):
        response = self.client.get("/clientes/", headers=self._headers(self.inactive_user))
        self.assertEqual(response.status_code, 403)

    def test_empresa_bloqueada_nao_opera(self):
        response = self.client.get("/clientes/", headers=self._headers(self.blocked_admin))
        self.assertEqual(response.status_code, 403)

    def test_empresa_somente_leitura_nao_altera_dados(self):
        response = self.client.post(
            "/clientes/",
            json={"nome": "Novo", "telefone": "444"},
            headers=self._headers(self.read_only_admin),
        )
        self.assertEqual(response.status_code, 403)

    def test_observador_nao_gera_fila_whatsapp(self):
        response = self.client.post(
            "/integracoes/n8n/whatsapp/fila/gerar",
            json={"tipo": "manual", "customer_id": self.customer.id, "mensagem_template": "Ola {nome}"},
            headers=self._headers(self.observer),
        )
        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    unittest.main()
