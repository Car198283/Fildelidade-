import os
import tempfile
import unittest
import hashlib
import hmac
import json
from pathlib import Path

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(tempfile.gettempdir()) / "fidelidade_authorization_test.db")
os.environ["SECRET_KEY"] = "test-secret-key-for-authorization-suite"

from fastapi.testclient import TestClient

from app.database import SessionLocal, engine
from app.main import app
from app.config import settings
from app.models import Base, Company, Customer, PointsTransaction, PromotionConfig, User, WhatsAppMessage
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
        self.assertEqual(data["company"]["cnpj"], "12345678000190")
        self.assertEqual(data["admin"]["role"], "admin")

        promotion = (
            self.db.query(PromotionConfig)
            .filter(PromotionConfig.company_id == data["company"]["id"])
            .first()
        )
        self.assertIsNotNone(promotion)

    def test_master_nao_cria_empresa_com_cnpj_duplicado(self):
        self.company.cnpj = "12345678000190"
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

    def test_master_nao_exclui_empresa_com_movimentacao(self):
        transaction = PointsTransaction(
            customer_id=self.customer.id,
            company_id=self.company.id,
            pontos=1,
            tipo="entrada",
            descricao="Teste",
            user_id=self.admin.id,
            origem="test",
            motivo="Teste de exclusao",
        )
        self.db.add(transaction)
        self.db.commit()

        response = self.client.delete(
            f"/admin/companies/{self.company.id}",
            headers=self._headers(self.master),
        )
        self.assertEqual(response.status_code, 400)

    def test_master_exclui_empresa_com_dados_quando_confirmado(self):
        company_id = self.company.id
        customer_id = self.customer.id
        transaction = PointsTransaction(
            customer_id=customer_id,
            company_id=company_id,
            pontos=1,
            tipo="entrada",
            descricao="Teste",
            user_id=self.admin.id,
            origem="test",
            motivo="Teste de exclusao forcada",
        )
        self.db.add(transaction)
        self.db.commit()

        response = self.client.delete(
            f"/admin/companies/{company_id}?force=true",
            headers=self._headers(self.master),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(self.db.query(Company).filter(Company.id == company_id).first())
        self.assertIsNone(self.db.query(Customer).filter(Customer.id == customer_id).first())

    def test_master_exclui_empresa_sem_movimentacao(self):
        create_response = self.client.post(
            "/admin/companies",
            json={
                "razao_social": "Empresa Sem Movimento LTDA",
                "nome": "Empresa Sem Movimento",
                "cnpj": "98.765.432/0001-10",
                "telefone": "(32) 98888-7777",
                "email": "contato-sem-movimento@example.com",
                "responsavel": "Joao Silva",
                "admin_email": "admin-sem-movimento@example.com",
                "admin_senha": "1234567890",
            },
            headers=self._headers(self.master),
        )
        self.assertEqual(create_response.status_code, 201)
        company_id = create_response.json()["data"]["company"]["id"]

        delete_response = self.client.delete(
            f"/admin/companies/{company_id}",
            headers=self._headers(self.master),
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertIsNone(self.db.query(Company).filter(Company.id == company_id).first())

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
        headers = self._headers(self.observer)
        headers["Idempotency-Key"] = "observer-denied-001"
        response = self.client.post(
            "/integracoes/n8n/whatsapp/fila/gerar",
            json={"tipo": "manual", "customer_id": self.customer.id, "mensagem_template": "Ola {nome}"},
            headers=headers,
        )
        self.assertEqual(response.status_code, 403)

    def test_whatsapp_n8n_e_idempotente_autenticado_e_isolado(self):
        headers = self._headers(self.admin)
        headers["Idempotency-Key"] = "campanha-agosto-001"
        body = {
            "tipo": "manual",
            "customer_id": self.customer.id,
            "mensagem_template": "Ola {nome}, voce tem {pontos} pontos",
            "max_attempts": 3,
        }
        first = self.client.post("/integracoes/n8n/whatsapp/fila/gerar", json=body, headers=headers)
        second = self.client.post("/integracoes/n8n/whatsapp/fila/gerar", json=body, headers=headers)
        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual(first.json()["data"][0]["id"], second.json()["data"][0]["id"])
        self.assertEqual(self.db.query(WhatsAppMessage).count(), 1)

        previous_secret = settings.n8n_webhook_secret
        settings.n8n_webhook_secret = "n8n-test-secret-with-at-least-32-characters"
        try:
            denied = self.client.post(
                "/integracoes/n8n/whatsapp/fila/consumir",
                json={"limit": 10},
                headers={"X-N8N-Secret": "segredo-invalido", "X-Company-Id": str(self.company.id)},
            )
            self.assertEqual(denied.status_code, 401)

            consumed = self.client.post(
                "/integracoes/n8n/whatsapp/fila/consumir",
                json={"limit": 10},
                headers={"X-N8N-Secret": settings.n8n_webhook_secret, "X-Company-Id": str(self.company.id)},
            )
            self.assertEqual(consumed.status_code, 200, consumed.text)
            self.assertEqual(consumed.json()["total"], 1)
            message_id = consumed.json()["data"][0]["id"]
            self.assertEqual(consumed.json()["data"][0]["status"], "processando")

            callback = self.client.post(
                f"/integracoes/n8n/whatsapp/fila/{message_id}/callback",
                json={"status": "enviado", "provider_message_id": "wamid.123"},
                headers={"X-N8N-Secret": settings.n8n_webhook_secret, "X-Company-Id": str(self.company.id)},
            )
            self.assertEqual(callback.status_code, 200, callback.text)
            self.assertEqual(callback.json()["data"]["status"], "enviado")

            other_company = self.client.post(
                "/integracoes/n8n/whatsapp/fila/consumir",
                json={"limit": 10},
                headers={"X-N8N-Secret": settings.n8n_webhook_secret, "X-Company-Id": str(self.other_company.id)},
            )
            self.assertEqual(other_company.json()["total"], 0)
        finally:
            settings.n8n_webhook_secret = previous_secret

    def test_webhook_meta_valida_assinatura_e_atualiza_status(self):
        previous_verify = settings.meta_webhook_verify_token
        previous_secret = settings.meta_app_secret
        settings.meta_webhook_verify_token = "verify-token-meta-test"
        settings.meta_app_secret = "meta-app-secret-test-value"
        self.company.whatsapp_phone_number_id = "123456789012345"
        queued = WhatsAppMessage(
            company_id=self.company.id,
            customer_id=self.customer.id,
            tipo="manual",
            telefone="5511999999999",
            mensagem="Teste",
            status="enviado",
            provider_message_id="wamid.meta-test",
        )
        self.db.add(queued)
        self.db.commit()
        try:
            verify = self.client.get(
                "/integracoes/meta/whatsapp/webhook",
                params={
                    "hub.mode": "subscribe",
                    "hub.challenge": "challenge-123",
                    "hub.verify_token": settings.meta_webhook_verify_token,
                },
            )
            self.assertEqual(verify.status_code, 200, verify.text)
            self.assertEqual(verify.text, "challenge-123")

            payload = {
                "entry": [{"changes": [{"value": {
                    "metadata": {"phone_number_id": "123456789012345"},
                    "statuses": [{"id": "wamid.meta-test", "status": "delivered"}],
                }}]}]
            }
            raw = json.dumps(payload, separators=(",", ":")).encode()
            signature = "sha256=" + hmac.new(
                settings.meta_app_secret.encode(), raw, hashlib.sha256
            ).hexdigest()
            denied = self.client.post(
                "/integracoes/meta/whatsapp/webhook",
                content=raw,
                headers={"Content-Type": "application/json", "X-Hub-Signature-256": "sha256=invalida"},
            )
            self.assertEqual(denied.status_code, 401)

            accepted = self.client.post(
                "/integracoes/meta/whatsapp/webhook",
                content=raw,
                headers={"Content-Type": "application/json", "X-Hub-Signature-256": signature},
            )
            self.assertEqual(accepted.status_code, 200, accepted.text)
            self.assertEqual(accepted.json()["updated"], 1)
            self.db.refresh(queued)
            self.assertEqual(queued.status, "entregue")
        finally:
            settings.meta_webhook_verify_token = previous_verify
            settings.meta_app_secret = previous_secret

    def test_admin_exclui_usuario_da_empresa(self):
        response = self.client.delete(
            f"/admin/users/{self.operator.id}",
            headers=self._headers(self.admin),
        )
        self.assertEqual(response.status_code, 200)

        self.db.refresh(self.operator)
        self.assertFalse(self.operator.ativo)
        self.assertIsNotNone(self.operator.excluido_em)

        listed = self.client.get("/admin/users", headers=self._headers(self.admin))
        listed_ids = {item["id"] for item in listed.json()["data"]}
        self.assertNotIn(self.operator.id, listed_ids)

    def test_login_ignora_maiusculas_e_espacos_no_email(self):
        self.operator.email = "Carlos.Eduardo@Example.Com"
        self.operator.exigir_troca_senha = True
        self.db.commit()

        response = self.client.post(
            "/auth/login",
            json={"email": "  carlos.eduardo@example.com  ", "senha": "1234567890"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["data"]["exigir_troca_senha"])

    def test_email_de_usuario_excluido_pode_ser_recadastrado(self):
        original_email = self.operator.email
        deleted = self.client.delete(
            f"/admin/users/{self.operator.id}", headers=self._headers(self.admin)
        )
        self.assertEqual(deleted.status_code, 200, deleted.text)

        created = self.client.post(
            "/admin/users",
            json={
                "nome": "Novo Operador",
                "email": original_email.upper(),
                "senha": "temporaria123",
                "role": "operador_captura",
            },
            headers=self._headers(self.admin),
        )
        self.assertEqual(created.status_code, 200, created.text)
        self.assertEqual(created.json()["data"]["email"], original_email)

    def test_admin_nao_exclui_proprio_usuario(self):
        response = self.client.delete(
            f"/admin/users/{self.admin.id}",
            headers=self._headers(self.admin),
        )
        self.assertEqual(response.status_code, 400)

    def test_admin_corrige_email_do_usuario(self):
        response = self.client.put(
            f"/admin/users/{self.operator.id}",
            json={"email": "  Carlos.Correto@Example.Com  ", "motivo": "Correcao cadastral"},
            headers=self._headers(self.admin),
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["data"]["email"], "carlos.correto@example.com")

        login = self.client.post(
            "/auth/login",
            json={"email": "CARLOS.CORRETO@EXAMPLE.COM", "senha": "1234567890"},
        )
        self.assertEqual(login.status_code, 200, login.text)

    def test_admin_nao_pode_repetir_email_de_outro_usuario(self):
        response = self.client.put(
            f"/admin/users/{self.operator.id}",
            json={"email": self.observer.email.upper(), "motivo": "Correcao cadastral"},
            headers=self._headers(self.admin),
        )
        self.assertEqual(response.status_code, 400, response.text)
        self.assertIn("Email ja cadastrado", response.json()["detail"])

    def test_ultimo_administrador_ativo_nao_pode_ser_desativado(self):
        response = self.client.put(
            f"/admin/users/{self.admin.id}",
            json={"ativo": False, "motivo": "Teste de protecao"},
            headers=self._headers(self.master),
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("administrador ativo", response.json()["detail"])

    def test_criacao_usuario_registra_nome_auditoria_e_troca_senha(self):
        response = self.client.post(
            "/admin/users",
            json={
                "nome": "Maria Operadora",
                "email": "maria@example.com",
                "senha": "temporaria123",
                "role": "operador_captura",
                "exigir_troca_senha": True,
            },
            headers=self._headers(self.admin),
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["data"]["nome"], "Maria Operadora")
        self.assertTrue(response.json()["data"]["exigir_troca_senha"])

        history = self.client.get(
            "/admin/users/audit/history", headers=self._headers(self.admin)
        )
        self.assertEqual(history.status_code, 200, history.text)
        self.assertEqual(history.json()["data"][0]["acao"], "criacao")

    def test_usuario_altera_senha_temporaria(self):
        self.operator.exigir_troca_senha = True
        self.db.commit()
        response = self.client.post(
            "/auth/change-password",
            json={"senha_atual": "1234567890", "nova_senha": "nova-senha-segura"},
            headers=self._headers(self.operator),
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.db.refresh(self.operator)
        self.assertFalse(self.operator.exigir_troca_senha)
        self.assertTrue(AuthService.verify_password("nova-senha-segura", self.operator.senha_hash))

    def test_promocao_avancada_cria_auditoria_e_simula(self):
        payload = {
            "tipo": "valor",
            "nome": "Bonus por valor",
            "valor_gasto": 100,
            "pontos_por_valor": 10,
            "descricao": "A cada R$ 100, ganhe 10 pontos.",
            "ativo": True,
            "acumulavel": True,
            "prioridade": 10,
            "valor_minimo_compra": 50,
            "recompensa_tipo": "pontos",
            "motivo_alteracao": "Criacao em teste",
        }
        created = self.client.post(
            "/promocoes/config", json=payload, headers=self._headers(self.admin)
        )
        self.assertEqual(created.status_code, 200, created.text)
        self.assertEqual(created.json()["data"]["situacao"], "ativa")

        simulation = self.client.post(
            "/promocoes/simular",
            json={"compras": 1, "valor_compra": 250},
            headers=self._headers(self.admin),
        )
        self.assertEqual(simulation.status_code, 200, simulation.text)
        self.assertEqual(simulation.json()["data"]["pontos_totais"], 20)

        history = self.client.get(
            "/promocoes/historico", headers=self._headers(self.admin)
        )
        self.assertEqual(history.status_code, 200, history.text)
        self.assertEqual(history.json()["data"][0]["motivo"], "Criacao em teste")

    def test_promocao_respeita_isolamento_da_empresa(self):
        self.db.add(PromotionConfig(
            company_id=self.other_company.id,
            tipo="quantidade",
            quantidade_produtos=2,
            pontos_por_quantidade=5,
            descricao="Outra empresa",
            ativo=True,
        ))
        self.db.commit()

        response = self.client.get(
            "/promocoes/configs", headers=self._headers(self.admin)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 0)


if __name__ == "__main__":
    unittest.main()
