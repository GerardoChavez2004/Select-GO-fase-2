%sql
-- Ricardo
SELECT t.nombre_supermercado,
       p.nombre_producto,
       c.nombre_tipo_movimiento AS motivo_merma, 
       SUM(m.cantidad) AS unidades_merma,
       RANK() OVER (
           PARTITION BY c.nombre_tipo_movimiento  
           ORDER BY SUM(m.cantidad) DESC
       ) AS ranking_por_motivo
FROM selectgo_fase2.silver.movimientos_clean m
JOIN selectgo_fase2.gold.dim_tienda t ON t.id_supermercado = m.id_supermercado
JOIN selectgo_fase2.gold.dim_producto p ON p.id_producto = m.id_producto
JOIN selectgo_fase2.gold.dim_tipo_movimiento c ON c.id_tipo_movimiento = m.id_tipo_movimiento
WHERE m.naturaleza_movimiento = 'SALIDA'
  AND c.es_merma = TRUE
GROUP BY t.nombre_supermercado, p.nombre_producto, c.nombre_tipo_movimiento
ORDER BY c.nombre_tipo_movimiento, unidades_merma DESC; 