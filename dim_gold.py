# Dimensión Canal
dim_canal = (
    spark.table(T_VENTAS_CL)
    .select("id_canal_venta", "nombre_canal", "descripcion_canal")
    .dropDuplicates(["id_canal_venta"])
)
dim_canal.write.mode("overwrite").saveAsTable(T_DIM_CANAL)

# Dimensión Producto (lectura individual + PySpark JOIN)
df_p = read_pg("public.producto")
df_cp = read_pg("public.categoria_producto")
df_m = read_pg("public.marca")

dim_producto = (
    df_p.alias("p")
    .join(df_cp.alias("cp"), F.col("p.id_categoria") == F.col("cp.id_categoria"), "inner")
    .join(df_m.alias("m"), F.col("p.id_marca") == F.col("m.id_marca"), "left")
    .select(
        "p.id_producto",
        "p.sku",
        "p.nombre_producto",
        "p.unidad_medida",
        "p.precio_unitario_referencia",
        "p.estado_producto",
        "cp.nombre_categoria",
        "m.nombre_marca"
    )
)
dim_producto.write.mode("overwrite").saveAsTable(T_DIM_PROD)

# Dimensión Tienda
dim_tienda = read_pg("public.supermercado").select(
    "id_supermercado", "nombre_supermercado", "direccion", "ciudad", "departamento", "estado"
)
dim_tienda.write.mode("overwrite").saveAsTable(T_DIM_TIENDA)

# Dimensión Fecha
dim_fecha = (
    spark.table(T_VENTAS_CL)
    .select(F.to_date("fecha_hora_venta").alias("fecha"))
    .dropDuplicates()
    .withColumn("anio", F.year("fecha"))
    .withColumn("mes", F.month("fecha"))
    .withColumn("dia", F.dayofmonth("fecha"))
    .withColumn("dia_semana", F.date_format("fecha", "EEEE"))
)
dim_fecha.write.mode("overwrite").saveAsTable(T_DIM_FECHA)

for t in (T_DIM_CANAL, T_DIM_PROD, T_DIM_TIENDA, T_DIM_FECHA):
    print(t, "->", spark.table(t).count(), "filas")
