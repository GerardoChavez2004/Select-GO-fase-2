def profiling_bronze(table_name, primary_key):
    df = spark.table(table_name)
    total_count = df.count()
    null_exprs = [F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df.columns]
    null_counts = df.select(null_exprs).collect()[0].asDict()
    duplicates = df.groupBy(primary_key).count().filter("count > 1").count()
    
    print(f"=== DATA PROFILING BRONZE: {table_name} ===")
    print(f"Total registros: {total_count} | Duplicados por clave '{primary_key}': {duplicates}")
    print("Nulos por columna:")
    for col_name, n_nulls in null_counts.items():
        pct = (n_nulls / total_count * 100) if total_count > 0 else 0
        if n_nulls > 0:
            print(f"  - {col_name}: {n_nulls} ({pct:.2f}%)")
    print("-" * 60)

# 1. Profiling explícito de las fuentes crudas
profiling_bronze(T_VENTAS_RAW, "id_detalle_venta")
profiling_bronze(T_MOV_RAW, "id_movimiento_inventario")
profiling_bronze(T_EXT_RAW, "retID" if "retID" in spark.table(T_EXT_RAW).columns else spark.table(T_EXT_RAW).columns[0])

# 2. Resumen consolidado por arquitectura Medallion
print("\n--- RESUMEN GENERAL DE FILAS POR CAPA ---")
print("CAPA BRONZE:")
for t in (T_VENTAS_RAW, T_MOV_RAW, T_EXT_RAW):
    print(f"  {t}: {spark.table(t).count()} filas")

print("CAPA SILVER:")
for t in (T_VENTAS_CL, T_VENTAS_QT, T_MOV_CL, T_MOV_QT, T_BENCHMARK):
    print(f"  {t}: {spark.table(t).count()} filas")

print("CAPA GOLD:")
for t in (T_DIM_CANAL, T_DIM_PROD, T_DIM_TIENDA, T_DIM_FECHA, T_FACT_VENT, T_INVENTARIO):
    print(f"  {t}: {spark.table(t).count()} filas")