UPDATE companies
SET cnpj = regexp_replace(cnpj, '\D', '', 'g')
WHERE cnpj IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_companies_cnpj
ON companies (cnpj)
WHERE cnpj IS NOT NULL AND cnpj != '';

ALTER TABLE customers
  ALTER COLUMN pontos TYPE NUMERIC(12, 2) USING pontos::numeric,
  ALTER COLUMN valor_gasto_atual TYPE NUMERIC(12, 2) USING valor_gasto_atual::numeric,
  ALTER COLUMN meta_premiacao_valor TYPE NUMERIC(12, 2) USING meta_premiacao_valor::numeric;

ALTER TABLE points_transactions
  ALTER COLUMN pontos TYPE NUMERIC(12, 2) USING pontos::numeric;

ALTER TABLE products
  ALTER COLUMN preco TYPE NUMERIC(12, 2) USING preco::numeric;

ALTER TABLE promotion_configs
  ALTER COLUMN pontos_por_quantidade TYPE NUMERIC(12, 2) USING pontos_por_quantidade::numeric,
  ALTER COLUMN valor_gasto TYPE NUMERIC(12, 2) USING valor_gasto::numeric,
  ALTER COLUMN pontos_por_valor TYPE NUMERIC(12, 2) USING pontos_por_valor::numeric,
  ALTER COLUMN percentual TYPE NUMERIC(5, 2) USING percentual::numeric;
