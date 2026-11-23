-- LNNL — garantias no banco de dados (referência).
-- O formato DEVE ser imposto também no armazenamento: validações de aplicação não cobrem
-- importações, scripts e gravações diretas. Armazene SEMPRE a forma canônica (14 caracteres,
-- maiúsculas, sem hífen); a máscara LNNL-LNNL-LNL-LNL é só de exibição.

-- ---------------------------------------------------------------- PostgreSQL
-- Verificadores (mód. 79) em SQL puro, para CHECK e para auditoria de dados legados.
CREATE OR REPLACE FUNCTION lnnl_valido(id text, tipo text DEFAULT NULL)
RETURNS boolean
LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS $$
  WITH c AS (SELECT id AS s),
  dados AS (SELECT substr(s, 1, 5) || substr(s, 8, 7) AS d, s FROM c),
  pesos(i, p) AS (VALUES (1,71),(2,63),(3,76),(4,57),(5,31),(6,1),(7,11),(8,15),(9,37),(10,13),(11,58),(12,2)),
  soma AS (
    SELECT sum(p * CASE WHEN substr(d, i, 1) BETWEEN 'A' AND 'Z'
                        THEN ascii(substr(d, i, 1)) - 64
                        ELSE ascii(substr(d, i, 1)) - 48 END) % 79 AS r
    FROM dados, pesos
  )
  SELECT (SELECT s FROM c) ~ '^[A-Z][1-9]{2}[A-Z]{2}[1-9]{2}[A-Z]{2}[1-9][A-Z]{2}[1-9][A-Z]$'
     AND substr((SELECT s FROM c), 2, 2) <> '93'
     AND (tipo IS NULL OR substr((SELECT s FROM c), 2, 2) = tipo)
     AND substr((SELECT s FROM c), 6, 2) = ((r / 9) + 1)::text || ((r % 9) + 1)::text
  FROM soma;
$$;

-- Exemplo: tabela de pedidos com tipo 22.
-- ALTER TABLE pedido
--   ADD COLUMN id_interno char(14) UNIQUE,
--   ADD CONSTRAINT chk_pedido_id_interno CHECK (id_interno IS NULL OR lnnl_valido(id_interno, '22'));
-- SELECT lnnl_valido('K12WF22MT5RQ7L');  -- true

-- ---------------------------------------------------------------- MySQL 8.0.16+ / MariaDB 10.2+
-- O CHECK com expressão regular garante o formato e o tipo; os verificadores ficam a cargo
-- da aplicação (ou de um gatilho). Use collation binária/sensível a maiúsculas na coluna.
-- ALTER TABLE pedido
--   ADD COLUMN id_interno CHAR(14) CHARACTER SET ascii COLLATE ascii_bin NULL UNIQUE,
--   ADD CONSTRAINT chk_pedido_id_interno CHECK (
--     id_interno IS NULL OR (
--       id_interno REGEXP '^[A-Z][1-9]{2}[A-Z]{2}[1-9]{2}[A-Z]{2}[1-9][A-Z]{2}[1-9][A-Z]$'
--       AND SUBSTRING(id_interno, 2, 2) = '22'
--     )
--   );

-- ---------------------------------------------------------------- SQLite
-- SQLite não tem REGEXP nativo; use GLOB, que cobre as classes de caractere:
-- CHECK (id_interno GLOB '[A-Z][1-9][1-9][A-Z][A-Z][1-9][1-9][A-Z][A-Z][1-9][A-Z][A-Z][1-9][A-Z]'
--        AND substr(id_interno, 2, 2) = '22')

-- ---------------------------------------------------------------- Inserção sem condição de corrida
-- Não faça "SELECT EXISTS" seguido de INSERT. Insira e, se a restrição UNIQUE falhar,
-- gere outro identificador e tente de novo (limite de tentativas, ex.: 5), dentro de transação.
