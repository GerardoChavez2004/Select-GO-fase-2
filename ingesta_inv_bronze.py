# Ingesta de la tabla movimientos_inventario a Bronze
df_mov_raw = read_pg("public.movimiento_inventario")  # Revisa si en PostgreSQL se llama 'movimiento_inventario' o 'movimientos_inventario'
df_mov_raw.write.mode("overwrite").saveAsTable(T_MOV_RAW)

print("Bronze movimientos_inventario_raw:", spark.table(T_MOV_RAW).count(), "filas")
