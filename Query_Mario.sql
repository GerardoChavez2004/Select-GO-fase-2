%sql
--Mario
SELECT 
    t.nombre_supermercado, 
    p.nombre_producto,
    i.stock_calculado AS stock_teorico_calculado,
    i.stock_actual AS stock_disponible_real,
    i.stock_minimo,
    i.stock_maximo,
    (i.stock_minimo - i.stock_actual) AS unidades_a_reponer,
    i.flag_inconsistencia_stock,
    RANK() OVER (ORDER BY (i.stock_minimo - i.stock_actual) DESC) AS ranking_urgencia
FROM selectgo_fase2.gold.inventario_actual i
JOIN selectgo_fase2.gold.dim_tienda t ON t.id_supermercado = i.id_supermercado
JOIN selectgo_fase2.gold.dim_producto p ON p.id_producto = i.id_producto
WHERE i.stock_actual < i.stock_minimo
ORDER BY unidades_a_reponer DESC;
