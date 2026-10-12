# 1. Leer la tabla base de inventario desde PostgreSQL (contiene el stock base)
df_inv_base = read_pg("public.inventario")

# 2. Agrupar los movimientos procesados de la capa Silver por tienda y producto
df_mov_agg = (
    spark.table(T_MOV_CL)
    .groupBy("id_supermercado", "id_producto")
    .agg(
        F.sum(
            F.when(F.col("naturaleza_movimiento") == "ENTRADA", F.col("cantidad"))
             .when(F.col("naturaleza_movimiento") == "SALIDA", -F.col("cantidad"))
             .otherwise(0)
        ).alias("neto_movimientos"),
        F.max("fecha_hora_movimiento").alias("ultimo_movimiento")
    )
)

# 3. Unir inventario base con el acumulado de movimientos
inventario_reconstruido = (
    df_inv_base.alias("inv")
    .join(
        df_mov_agg.alias("mov"),
        (F.col("inv.id_supermercado") == F.col("mov.id_supermercado")) &
        (F.col("inv.id_producto") == F.col("mov.id_producto")),
        "left"
    )
    .select(
        F.col("inv.id_inventario"),
        F.col("inv.id_supermercado"),
        F.col("inv.id_producto"),
        F.col("inv.stock_actual").alias("stock_base"),
        F.coalesce(F.col("mov.neto_movimientos"), F.lit(0)).alias("neto_movimientos"),
        # Stock teórico calculado = stock base + entradas - salidas
        (F.col("inv.stock_actual") + F.coalesce(F.col("mov.neto_movimientos"), F.lit(0))).alias("stock_calculado"),
        F.col("inv.stock_minimo"),
        F.col("inv.stock_maximo"),
        F.col("mov.ultimo_movimiento")
    )
)

# 4. Saneamiento: piso en 0 para stock disponible y creación del flag de inconsistencia
inventario_final = (
    inventario_reconstruido
    .withColumn("stock_actual", F.when(F.col("stock_calculado") < 0, F.lit(0)).otherwise(F.col("stock_calculado")))
    .withColumn("flag_inconsistencia_stock", F.when(F.col("stock_calculado") < 0, F.lit(True)).otherwise(F.lit(False)))
    .withColumn("generado_at", F.current_timestamp())
)

# 5. Guardar en la capa Gold
inventario_final.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(T_INVENTARIO)

print("inventario_actual reconstruido y saneado:", spark.table(T_INVENTARIO).count(), "filas")
display(spark.table(T_INVENTARIO).orderBy("stock_calculado").limit(10))