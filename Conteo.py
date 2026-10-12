conteo_supabase = read_pg("SELECT COUNT(*) AS total FROM detalle_venta").collect()[0]["total"]
conteo_bronze = spark.table(T_VENTAS_RAW).count()
conteo_gold = spark.table(T_FACT_VENT).count()
conteo_cuarentena = spark.table(T_VENTAS_QT).count()

print(f"Supabase (fuente real):     {conteo_supabase}")
print(f"Bronze (extraído):          {conteo_bronze}")
print(f"Gold (limpio) + Cuarentena: {conteo_gold} + {conteo_cuarentena} = {conteo_gold + conteo_cuarentena}")
print("Íntegro:", conteo_supabase == conteo_bronze == (conteo_gold + conteo_cuarentena))