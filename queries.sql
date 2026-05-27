-- ============================================================
-- Анализ финансовой отчётности компаний
-- SQL-запросы для PostgreSQL
-- ============================================================

-- 1. Создание таблицы
CREATE TABLE IF NOT EXISTS financials (
    id          SERIAL PRIMARY KEY,
    company     VARCHAR(100),
    year        INTEGER,
    revenue     NUMERIC,
    net_income  NUMERIC,
    total_assets NUMERIC,
    total_liabilities NUMERIC
);

-- Загрузка данных из CSV (выполнить в psql):
-- \COPY financials(company, year, revenue, net_income, total_assets, total_liabilities)
-- FROM 'financial_statements.csv' CSV HEADER;

-- ============================================================
-- 2. Топ-10 компаний по выручке за последний год
-- ============================================================
SELECT
    company,
    revenue / 1e9              AS revenue_bln,
    net_income / 1e9           AS net_income_bln,
    ROUND(net_income / revenue * 100, 2) AS net_margin_pct
FROM financials
WHERE year = (SELECT MAX(year) FROM financials)
ORDER BY revenue DESC
LIMIT 10;

-- ============================================================
-- 3. Средняя рентабельность по годам
-- ============================================================
SELECT
    year,
    COUNT(DISTINCT company)                        AS companies_count,
    ROUND(AVG(revenue) / 1e9, 2)                  AS avg_revenue_bln,
    ROUND(AVG(net_income / revenue * 100), 2)     AS avg_net_margin_pct,
    ROUND(AVG(net_income / total_assets * 100), 2) AS avg_roa_pct
FROM financials
WHERE revenue > 0
GROUP BY year
ORDER BY year;

-- ============================================================
-- 4. Топ-10 компаний по ROA (рентабельность активов)
-- ============================================================
SELECT
    company,
    ROUND(net_income / total_assets * 100, 2) AS roa_pct,
    ROUND(net_income / revenue * 100, 2)      AS net_margin_pct
FROM financials
WHERE year = (SELECT MAX(year) FROM financials)
  AND total_assets > 0
  AND revenue > 0
ORDER BY roa_pct DESC
LIMIT 10;

-- ============================================================
-- 5. Компании с устойчивым ростом выручки (3+ года подряд)
-- ============================================================
WITH revenue_growth AS (
    SELECT
        company,
        year,
        revenue,
        LAG(revenue) OVER (PARTITION BY company ORDER BY year) AS prev_revenue
    FROM financials
),
growth_flag AS (
    SELECT
        company,
        year,
        CASE WHEN revenue > prev_revenue THEN 1 ELSE 0 END AS grew
    FROM revenue_growth
    WHERE prev_revenue IS NOT NULL
)
SELECT company, SUM(grew) AS growth_years
FROM growth_flag
GROUP BY company
HAVING SUM(grew) >= 10
ORDER BY growth_years DESC;
