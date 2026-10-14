# 1. Lectura de catálogos desde PostgreSQL usando el nombre exacto
df_inv = read_pg("public.inventario")
df_tm = read_pg("public.tipo_movimiento_inventario")

# 2. Enriquecimiento del dataframe Bronze
df_mov_enriched = (
    spark.table(T_MOV_RAW).alias("m")
    .join(df_inv.alias("i"), F.col("m.id_inventario") == F.col("i.id_inventario"), "left")
    .join(df_tm.alias("tm"), F.col("m.id_tipo_movimiento") == F.col("tm.id_tipo_movimiento"), "left")
    .select(
        F.col("m.id_movimiento_inventario"),
        F.col("i.id_supermercado"),
        F.col("i.id_producto"),
        F.coalesce(F.col("tm.naturaleza_movimiento"), F.col("tm.nombre_tipo_movimiento")).alias("naturaleza_movimiento"),
        F.col("m.cantidad"),
        F.col("m.fecha_hora_movimiento"),
        F.col("m.observacion")
    )
)

# 3. Reglas de calidad y etiquetado para cuarentena
df_mov_annotated = (
    df_mov_enriched
    .withColumn("err_qty_invalid", (F.col("cantidad").isNull()) | (F.col("cantidad") <= 0))
    .withColumn("err_naturaleza_invalid", (F.col("naturaleza_movimiento").isNull()) | (~F.col("naturaleza_movimiento").isin("ENTRADA", "SALIDA")))
    .withColumn("err_fecha_null", F.col("fecha_hora_movimiento").isNull())
    .withColumn("rejection_reasons", F.concat_ws(";", 
        F.when(F.col("err_qty_invalid"), F.lit("INVALID_QUANTITY")),
        F.when(F.col("err_naturaleza_invalid"), F.lit("INVALID_NATURALEZA")),
        F.when(F.col("err_fecha_null"), F.lit("NULL_FECHA"))
    ))
)

# 4. Deduplicación por ventana
w2 = Window.partitionBy("id_movimiento_inventario").orderBy(F.col("fecha_hora_movimiento"))
df_mov_deduped = df_mov_annotated.withColumn("_rn", F.row_number().over(w2))

drop_cols2 = ["_rn", "err_qty_invalid", "err_naturaleza_invalid", "err_fecha_null"]

# 5. Filtrado de registros limpios y cuarentena
df_mov_clean = (
    df_mov_deduped.filter((F.length("rejection_reasons") == 0) & (F.col("_rn") == 1))
    .drop(*drop_cols2)
)

df_mov_quar = (
    df_mov_deduped.filter((F.length("rejection_reasons") > 0) | (F.col("_rn") > 1))
    .withColumn("quarantined_at", F.current_timestamp())
    .drop(*drop_cols2)
)

# 6. Guardar en capa Silver
df_mov_clean.write.mode("overwrite").saveAsTable(T_MOV_CL)
df_mov_quar.write.mode("overwrite").saveAsTable(T_MOV_QT)

print(f"Silver movimientos_clean: {spark.table(T_MOV_CL).count()} | movimientos_quarantine: {spark.table(T_MOV_QT).count()}")
display(spark.table(T_MOV_CL).limit(10))