%sql
--Gerardo
SELECT p1.nombre_producto AS producto_a, p2.nombre_producto AS producto_b,
       COUNT(*) AS veces_juntos
FROM selectgo_fase2.gold.fact_ventas f1
JOIN selectgo_fase2.gold.fact_ventas f2
  ON f1.id_venta = f2.id_venta AND f1.id_producto < f2.id_producto
JOIN selectgo_fase2.gold.dim_producto p1 ON p1.id_producto = f1.id_producto
JOIN selectgo_fase2.gold.dim_producto p2 ON p2.id_producto = f2.id_producto
GROUP BY p1.nombre_producto, p2.nombre_producto
ORDER BY veces_juntos DESC
LIMIT 15;