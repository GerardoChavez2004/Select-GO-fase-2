WITH clasificacion AS (
  SELECT id_producto, nombre_producto,
    CASE
      WHEN nombre_categoria = 'Limpieza del Hogar' THEN 'Limpieza'
      WHEN nombre_categoria = 'Cuidado Personal'   THEN 'Cuidado Personal'
      ELSE 'Comida y Bebidas'
    END AS grupo_producto
  FROM selectgo_fase2.gold.dim_producto
),
pares AS (
  SELECT c1.grupo_producto,
         p1.nombre_producto AS producto_a, p2.nombre_producto AS producto_b,
         COUNT(*) AS veces_juntos
  FROM selectgo_fase2.gold.fact_ventas f1
  JOIN selectgo_fase2.gold.fact_ventas f2
    ON f1.id_venta = f2.id_venta AND f1.id_producto < f2.id_producto
  JOIN clasificacion c1 ON c1.id_producto = f1.id_producto
  JOIN clasificacion c2 ON c2.id_producto = f2.id_producto
  JOIN selectgo_fase2.gold.dim_producto p1 ON p1.id_producto = f1.id_producto
  JOIN selectgo_fase2.gold.dim_producto p2 ON p2.id_producto = f2.id_producto
  WHERE c1.grupo_producto = c2.grupo_producto
  GROUP BY c1.grupo_producto, p1.nombre_producto, p2.nombre_producto
),
rankeado AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY grupo_producto ORDER BY veces_juntos DESC) AS puesto
  FROM pares
)
SELECT grupo_producto, puesto, producto_a, producto_b, veces_juntos
FROM rankeado
WHERE puesto <= 20          -- top 20 de CADA grupo, no 20 en total
ORDER BY grupo_producto, puesto;

--Query corregida por agrupación, se hace un promedio de los top de cada categoria y se busca una media para juntarlos