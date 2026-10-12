inventario_actual = (
    spark.table(T_MOV_CL)
    .withColumn("signo", F.when(F.col("naturaleza_movimiento") == "ENTRADA", F.col("cantidad"))
                           .otherwise(-F.col("cantidad")))
    .groupBy("id_supermercado", "id_producto")
    .agg(
        F.sum("signo").alias("stock_actual"),
        F.max("fecha_hora_movimiento").alias("ultimo_movimiento")
    )
    .withColumn("generado_at", F.current_timestamp())
)

inventario_actual.write.mode("overwrite").saveAsTable(T_INVENTARIO)
print("Gold inventario_actual:", spark.table(T_INVENTARIO).count(), "filas")
display(spark.table(T_INVENTARIO).orderBy("stock_actual").limit(10))