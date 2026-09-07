\echo '1. Nombre total de livres charges'
SELECT COUNT(*) AS total_books
FROM books;

\echo ''
\echo '2. Controle des doublons UPC'
SELECT upc, COUNT(*) AS occurrences
FROM books
GROUP BY upc
HAVING COUNT(*) > 1
ORDER BY occurrences DESC, upc ASC;

\echo ''
\echo '3. Controle des doublons URL produit'
SELECT product_url, COUNT(*) AS occurrences
FROM books
GROUP BY product_url
HAVING COUNT(*) > 1
ORDER BY occurrences DESC, product_url ASC;

\echo ''
\echo '4. Livres en rupture ou en stock faible'
SELECT
    upc,
    title,
    category,
    stock_quantity,
    stock_status,
    rating,
    price_incl_tax
FROM books_stock_alerts
ORDER BY stock_quantity ASC, rating DESC, title ASC
LIMIT 20;

\echo ''
\echo '5. Livres les mieux notes'
SELECT
    upc,
    title,
    category,
    rating,
    review_count,
    stock_quantity,
    price_incl_tax
FROM books_best_rated
ORDER BY rating DESC, review_count DESC, title ASC
LIMIT 20;

\echo ''
\echo '6. Repartition par categorie'
SELECT
    category,
    COUNT(*) AS total_books,
    MIN(price_incl_tax) AS min_price,
    MAX(price_incl_tax) AS max_price,
    ROUND(AVG(price_incl_tax), 2) AS avg_price
FROM books_catalog
GROUP BY category
ORDER BY total_books DESC, category ASC;

\echo ''
\echo '7. Controle prix et taxe'
SELECT
    COUNT(*) FILTER (WHERE price_list = price_excl_tax) AS list_equals_excl_tax,
    COUNT(*) FILTER (WHERE price_excl_tax = price_incl_tax) AS excl_tax_equals_incl_tax,
    COUNT(*) FILTER (WHERE tax = 0) AS tax_zero,
    COUNT(*) FILTER (
        WHERE price_list <> price_excl_tax
           OR price_excl_tax <> price_incl_tax
           OR tax <> 0
    ) AS price_or_tax_differences
FROM books_catalog;
