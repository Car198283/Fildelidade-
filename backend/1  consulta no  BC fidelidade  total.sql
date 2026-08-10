SELECT name
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;

SELECT * FROM points_transactions;
-- SELECT * FROM clientes;
-- 
-- CREATE TABLE clientes (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     nome TEXT NOT NULL,
--     email TEXT,
--     telefone TEXT,
--    data de nascimento TEXT,
--     data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);