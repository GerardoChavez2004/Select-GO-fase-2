fact_ventas = (
    spark.table(T_VENTAS_CL)
    .withColumn("fecha", F.to_date("fecha_hora_venta"))
    .select(
        "id_detalle_venta",
        "id_venta",
        "id_cliente",
        "id_supermercado",
        "id_canal_venta",
        "id_producto",
        "id_empleado",
        "fecha",
        "cantidad",
        "precio_unitario",
        "descuento_unitario",
        "subtotal_linea",
        "total_venta",
        "descuento_venta",
        "impuesto_venta"
    )
)

fact_ventas.write.mode("overwrite").saveAsTable(T_FACT_VENT)
print("Gold fact_ventas:", spark.table(T_FACT_VENT).count(), "filas")
display(spark.table(T_FACT_VENT).limit(10))
