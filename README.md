# Proyecto Integrador · Fase 2
## Arquitectura Medallion y Analítica de Datos para SelectGo

**Universidad Dr. José Matías Delgado**  
**Licenciatura en Innovación y Transformación Digital**  
**Materia:** Arquitectura de Datos en Entornos Digitales  
**Docente:** Ing. Jaime García Santos | **Ciclo:** II-2026  

---

## 👥 Integrantes
* **Fabricio Abrego Quijada** — Carnet: 202400644
* **Gerardo Chávez Guillén** — Carnet: 202401062
* **Ricardo Ramírez Escobar** — Carnet: 202401177
* **Mario Urquiza Funes** — Carnet: 202401197

---

## 📌 Resumen Ejecutivo
SelectGo aborda el análisis de ventas e inventario de un supermercado mediante una arquitectura analítica Medallion en Databricks. El pipeline consolida datos transaccionales desde PostgreSQL, mantiene la trazabilidad cruda en **Bronze**, aplica reglas de validación y cuarentena en **Silver**, y construye un modelo dimensional (hechos y dimensiones) en **Gold**. 

Además, consume una API REST pública (Zenodo) para incorporar un benchmark externo de precios por categoría y habilitar consultas OLAP de soporte a decisiones.

---

## 🏗️ Arquitectura Medallion y Flujo de Datos

1. **Capa Bronze (Ingesta Cruda):**
   - Lectura de tablas transaccionales de ventas, detalle de ventas, canales y movimientos de inventario desde PostgreSQL.
   - Consumo de la API REST de Zenodo (`GET https://zenodo.org/api/records/18342253`) para descargar metadatos y dataset de precios de referencia (`market_reference_raw`).

2. **Capa Silver (Limpieza, Calidad e Integración):**
   - **Ventas:** Identificación de anomalías (IDs nulos, precios o cantidades inválidos, descuadres de subtotal) y deduplicación por ventana. Registros anómalos enviados a `ventas_quarantine`.
   - **Movimientos:** Validación de naturaleza (`ENTRADA`/`SALIDA`), cantidades positivas y fechas no nulas.
   - **Benchmark Externo:** Mapeo de categorías locales (arroz, azúcar, lácteos) con datos de Zenodo y conversión de moneda PLN a USD (tasa ref: 0.25).

3. **Capa Gold (Modelo Analítico):**
   - Construcción de dimensiones (`dim_producto`, `dim_tienda`, `dim_canal`, `dim_fecha`).
   - Tabla de hechos `fact_ventas` para métricas comerciales.
   - Tabla `inventario_actual` con cálculo de stock teórico, saldo disponible y banderas de inconsistencia.

---

## 📊 Consultas OLAP Desarrolladas

* **Reposición Prioritaria (Mario Urquiza):** Identifica productos por debajo del stock mínimo ordenados por urgencia de reabastecimiento.
* **Salidas de Inventario (Ricardo Ramírez):** Agrupa y clasifica los movimientos de salida por tienda y producto.
* **Ticket Promedio por Tienda y Canal (Fabricio Abrego):** Reconstruye el importe por ticket y evalúa el desempeño entre canales de venta.
* **Asociación de Productos / Basket Analysis (Gerardo Chávez):** Realiza auto-join sobre ventas para identificar los pares de productos comprados conjuntamente con mayor frecuencia.

---

## ⚙️ Estructura del Catálogo Delta
Todas las tablas han sido persistidas en el catálogo `selectgo_fase2`:
* `selectgo_fase2.bronze.*`
* `selectgo_fase2.silver.*`
* `selectgo_fase2.gold.*`