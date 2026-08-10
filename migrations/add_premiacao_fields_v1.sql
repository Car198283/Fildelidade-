-- Migration: Adicionar campos de rastreamento de premiação ao Customer
-- Data: 12 de abril de 2026
-- Compatível com: PostgreSQL, SQLite, SQL Server

-- ============== PostgreSQL ==============
-- Se estiver usando PostgreSQL, execute:
-- ALTER TABLE customers ADD COLUMN IF NOT EXISTS valor_gasto_atual FLOAT DEFAULT 0.0 NOT NULL;
-- ALTER TABLE customers ADD COLUMN IF NOT EXISTS quantidade_produtos_comprados INTEGER DEFAULT 0 NOT NULL;
-- ALTER TABLE customers ADD COLUMN IF NOT EXISTS meta_premiacao_valor FLOAT DEFAULT NULL;
-- ALTER TABLE customers ADD COLUMN IF NOT EXISTS meta_premiacao_quantidade INTEGER DEFAULT NULL;
-- CREATE INDEX IF NOT EXISTS idx_customer_valor_gasto ON customers(valor_gasto_atual);
-- CREATE INDEX IF NOT EXISTS idx_customer_quantidade_produtos ON customers(quantidade_produtos_comprados);

-- ============== SQLite ==============
-- SQLite não suporta ALTER TABLE ADD COLUMN IF NOT EXISTS
-- Mas o ORM do SQLAlchemy cria automaticamente as colunas via migration
-- Você pode executar via:
-- PRAGMA table_info(customers);  -- para verificar colunas atuais

-- ============== SQL Server ==============
-- Para SQL Server, use:
-- IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='customers' AND COLUMN_NAME='valor_gasto_atual')
--   ALTER TABLE customers ADD valor_gasto_atual FLOAT DEFAULT 0.0 NOT NULL;
-- IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='customers' AND COLUMN_NAME='quantidade_produtos_comprados')
--   ALTER TABLE customers ADD quantidade_produtos_comprados INTEGER DEFAULT 0 NOT NULL;
-- IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='customers' AND COLUMN_NAME='meta_premiacao_valor')
--   ALTER TABLE customers ADD meta_premiacao_valor FLOAT NULL;
-- IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='customers' AND COLUMN_NAME='meta_premiacao_quantidade')
--   ALTER TABLE customers ADD meta_premiacao_quantidade INTEGER NULL;

-- ============== INSTRUÇÕES ==============
-- 1. Para SQLITE: As colunas serão criadas automaticamente ao usar o ORM
--    Só é necessário executar o backend que fará a criação automática
-- 2. Para POSTGRESQL: Execute os comandos ALTER TABLE acima
-- 3. Para SQL SERVER: Execute os comandos IF NOT EXISTS acima

-- Verificar Estrutura (universal):
SELECT COUNT(*) as total_customers FROM customers;

