%sql
-- Ricardo
SELECT t.nombre_supermercado, p.nombre_producto,
       SUM(m.cantidad) AS unidades_merma,
       RANK() OVER (ORDER BY SUM(m.cantidad) DESC) AS ranking_merma
FROM selectgo_fase2.silver.movimientos_clean m
JOIN selectgo_fase2.gold.dim_tienda t ON t.id_supermercado = m.id_supermercado
JOIN selectgo_fase2.gold.dim_producto p ON p.id_producto = m.id_producto
WHERE m.naturaleza_movimiento = 'SALIDA'
GROUP BY t.nombre_supermercado, p.nombre_producto
ORDER BY unidades_merma DESC;