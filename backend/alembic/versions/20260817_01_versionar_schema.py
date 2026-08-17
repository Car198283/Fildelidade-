"""Cria schema-base explicitamente e adiciona auditoria/idempotencia ao legado."""
from alembic import op
import sqlalchemy as sa

revision = "20260817_01"
down_revision = None
branch_labels = None
depends_on = None


def ts():
    return [sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime())]


def fresh_schema():
    op.create_table("companies",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("razao_social", sa.String(255)), sa.Column("cnpj", sa.String(14)), sa.Column("telefone", sa.String(30)),
        sa.Column("email", sa.String(255)), sa.Column("responsavel", sa.String(255)), sa.Column("cep", sa.String(20)),
        sa.Column("endereco", sa.String(255)), sa.Column("numero", sa.String(30)), sa.Column("bairro", sa.String(120)),
        sa.Column("cidade", sa.String(120)), sa.Column("estado", sa.String(2)), sa.Column("logotipo", sa.String(500)),
        sa.Column("plano", sa.String(50)), sa.Column("ativo", sa.Boolean()), sa.Column("read_only", sa.Boolean(), nullable=False),
        *ts(), sa.UniqueConstraint("cnpj", name="uq_companies_cnpj"))
    op.create_index("ix_companies_id", "companies", ["id"]); op.create_index("ix_companies_cnpj", "companies", ["cnpj"])
    op.create_table("users",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(255), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False), sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("role", sa.String(50)), sa.Column("ativo", sa.Boolean()), *ts(),
        sa.CheckConstraint("role IN ('master', 'admin', 'operador_captura', 'observador')", name="ck_users_role"),
        sa.UniqueConstraint("email", name="uq_users_email"))
    op.create_index("ix_users_id", "users", ["id"]); op.create_index("ix_users_email", "users", ["email"]); op.create_index("ix_users_company_id", "users", ["company_id"])
    op.create_table("customers",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("nome", sa.String(255), nullable=False), sa.Column("telefone", sa.String(20)),
        sa.Column("email", sa.String(255)), sa.Column("data_nascimento", sa.Date()), sa.Column("pontos", sa.Numeric(12, 2), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False), sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("valor_gasto_atual", sa.Numeric(12, 2), nullable=False), sa.Column("quantidade_produtos_comprados", sa.Integer(), nullable=False),
        sa.Column("meta_premiacao_valor", sa.Numeric(12, 2)), sa.Column("meta_premiacao_quantidade", sa.Integer()), *ts())
    for name, cols in (("ix_customers_id", ["id"]), ("ix_customers_company_id", ["company_id"]), ("idx_customer_company", ["company_id"]), ("idx_customer_nome", ["nome"]), ("idx_customer_telefone", ["telefone"]), ("idx_customer_data_nascimento", ["data_nascimento"])): op.create_index(name, "customers", cols)
    op.create_table("categories",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False), *ts())
    op.create_index("ix_categories_id", "categories", ["id"]); op.create_index("ix_categories_company_id", "categories", ["company_id"]); op.create_index("idx_category_company", "categories", ["company_id"])
    op.create_table("products",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("categoria_id", sa.Integer(), sa.ForeignKey("categories.id")), sa.Column("preco", sa.Numeric(12, 2), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False), *ts())
    op.create_index("ix_products_id", "products", ["id"]); op.create_index("ix_products_company_id", "products", ["company_id"]); op.create_index("idx_product_company", "products", ["company_id"]); op.create_index("idx_product_category", "products", ["categoria_id"])
    op.create_table("promotion_configs",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("tipo", sa.String(12), nullable=False), sa.Column("quantidade_produtos", sa.Integer()), sa.Column("pontos_por_quantidade", sa.Numeric(12, 2)),
        sa.Column("valor_gasto", sa.Numeric(12, 2)), sa.Column("pontos_por_valor", sa.Numeric(12, 2)), sa.Column("percentual", sa.Numeric(5, 2)),
        sa.Column("descricao", sa.String(500)), sa.Column("ativo", sa.Boolean(), nullable=False), *ts())
    op.create_index("ix_promotion_configs_id", "promotion_configs", ["id"]); op.create_index("ix_promotion_configs_company_id", "promotion_configs", ["company_id"]); op.create_index("idx_promotion_company", "promotion_configs", ["company_id"])
    op.create_table("points_transactions",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False), sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")),
        sa.Column("product_nome", sa.String(255)), sa.Column("pontos", sa.Numeric(12, 2), nullable=False), sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("descricao", sa.String(255)), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("origem", sa.String(50), nullable=False), sa.Column("motivo", sa.String(500), nullable=False), sa.Column("idempotency_key", sa.String(255)), *ts(),
        sa.UniqueConstraint("company_id", "idempotency_key", name="uq_points_company_idempotency"))
    for name, cols in (("ix_points_transactions_id", ["id"]), ("ix_points_transactions_customer_id", ["customer_id"]), ("ix_points_transactions_company_id", ["company_id"]), ("ix_points_transactions_product_id", ["product_id"]), ("ix_points_transactions_user_id", ["user_id"]), ("idx_transaction_customer", ["customer_id"]), ("idx_transaction_company", ["company_id"]), ("idx_transaction_product", ["product_id"]), ("idx_transaction_created", ["created_at"])): op.create_index(name, "points_transactions", cols)
    op.create_table("whatsapp_messages",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id")), sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("telefone", sa.String(30), nullable=False), sa.Column("cliente_nome", sa.String(255)), sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False), sa.Column("provider_message_id", sa.String(255)), sa.Column("erro", sa.Text()),
        sa.Column("scheduled_at", sa.DateTime()), sa.Column("sent_at", sa.DateTime()), *ts())
    for name, cols in (("ix_whatsapp_messages_id", ["id"]), ("ix_whatsapp_messages_company_id", ["company_id"]), ("ix_whatsapp_messages_customer_id", ["customer_id"]), ("ix_whatsapp_messages_tipo", ["tipo"]), ("ix_whatsapp_messages_telefone", ["telefone"]), ("ix_whatsapp_messages_status", ["status"]), ("idx_whatsapp_company_status", ["company_id", "status"]), ("idx_whatsapp_customer", ["customer_id"])): op.create_index(name, "whatsapp_messages", cols)


def upgrade_legacy():
    op.create_check_constraint("ck_users_role", "users", "role IN ('master', 'admin', 'operador_captura', 'observador')")
    for column in (sa.Column("user_id", sa.Integer()), sa.Column("origem", sa.String(50)), sa.Column("motivo", sa.String(500)), sa.Column("idempotency_key", sa.String(255))): op.add_column("points_transactions", column)
    op.create_foreign_key("fk_points_transactions_user", "points_transactions", "users", ["user_id"], ["id"])
    op.create_index("ix_points_transactions_user_id", "points_transactions", ["user_id"])
    op.create_unique_constraint("uq_points_company_idempotency", "points_transactions", ["company_id", "idempotency_key"])


def upgrade():
    if not sa.inspect(op.get_bind()).has_table("points_transactions"): fresh_schema()
    else: upgrade_legacy()


def downgrade():
    for table in ("whatsapp_messages", "points_transactions", "promotion_configs", "products", "categories", "customers", "users", "companies"): op.drop_table(table)
