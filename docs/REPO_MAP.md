# Compact AST Repository Map (Portfolio_Empresarial_PowerBI)
> **Propósito**: Mapa ultracompacto de símbolos, docstrings y conectividad para alimentar a agentes de IA con pocos tokens.
> **Directorios escaneados**: 01_Limpieza_de_Datos, 05_Analisis_Econometrico, tools (21 módulos)
> **'conectado'** = referenciado (import o nombre de archivo) desde otro lugar del repo. 'sin referencias externas' no implica código roto -- puede ser un script standalone válido que nadie documentó todavía en SKILL_ROUTER.md.

### [`01_generar_datos_historicos_ventas.py`](01_Limpieza_de_Datos/01_generar_datos_historicos_ventas.py) — ⚠️ sin referencias externas encontradas
> Genera datos crudos (raw) de ventas 2021-2025 para 36 SKUs, calibrados contra
- `cargar_series_reales()` (L102)
- `sucio_fecha(fecha, i)` — Reproduce la mezcla de formatos de fecha del archivo raw original. (L111)
- `sucio_texto(v, i)` — Ensucia levemente MATNR/INCO1 (case + espacios) como el archivo original. (L118)
- `generar()` (L129)
- `generar_maestro_productos()` (L205)

### [`02_generar_presupuesto_2025.py`](01_Limpieza_de_Datos/02_generar_presupuesto_2025.py) — 🔗 conectado
> Generador de Presupuesto Multianual 2021-2025 Indexado a Inflacion INDEC y Tipo de Cambio BCRA.
- `_drifts_por_segmento(seg, rng)` — Sesgo estructural de planificacion (fijo por SKU): crecimiento de volumen vs anio (L27)
- `generar_presupuesto_indexado()` (L37)

### [`03_etl_pipeline_cleaner.py`](01_Limpieza_de_Datos/03_etl_pipeline_cleaner.py) — ⚠️ sin referencias externas encontradas
> ===================================================================================
- `parse_date_robust(date_val)` — Parsea de forma robusta cadenas de fecha en diversos formatos a objeto datetime.date. (L33)
- `escanear_rango_fechas_observado(raw_dir)` — Recorre las fuentes transaccionales crudas (ventas, OPEX, remitos de planta, (L65)
- `clean_currency_or_number(val)` — Limpia cadenas numericas con simbolos monetarios, puntos de miles y comas decimales. (L99)
- `clean_string_col(series, case)` — Elimina espacios en blanco exteriores, multiples espacios interiores y ajusta mayusculas. (L122)
- `run_etl()` (L137)

### [`audit_suite03_operations.py`](01_Limpieza_de_Datos/audit_suite03_operations.py) — ⚠️ sin referencias externas encontradas
> Auditoria Integral de Modelado de Datos y TMDL para Suite 03 Operations
- `test_fact_operaciones_planta()` (L18)
- `test_fact_inventario_guarda()` (L38)
- `test_cuentas_contables_y_opex()` (L63)
- `test_semantic_model_tmdl()` (L87)
- `test_duckdb_integration()` (L128)

### [`test_business_value_sanity.py`](01_Limpieza_de_Datos/tests/test_business_value_sanity.py) — ⚠️ sin referencias externas encontradas
> Tests de VALOR DE NEGOCIO sobre curated_gold y outputs econometricos.
- `quality_report()` (L25)
- `ventas()` (L30)
- `productos()` (L35)
- `capital_trabajo()` (L40)
- `opex()` (L45)
- `test_sin_huerfanas_sin_resolver(quality_report)` — Toda clave huerfana detectada por el ETL debe haber sido resuelta (cuarentena/fix), no colada. (L50)
- `test_tasa_validez_alta(quality_report)` (L58)
- `test_ventas_referencian_productos_existentes(ventas, productos)` (L64)
- *...y 17 funciones más*

### [`update_data_layer.py`](01_Limpieza_de_Datos/update_data_layer.py) — ⚠️ sin referencias externas encontradas
> Script de Actualizacion de Capa de Datos y Modelos Semanticos
- `update_fact_operaciones_planta()` (L16)
- `create_fact_inventario_guarda()` (L51)
- `update_dim_cuentas_contables()` (L177)
- `update_fact_opex_mensual()` (L208)

### [`analisis_elasticidad_cointegracion.py`](05_Analisis_Econometrico/src/analisis_elasticidad_cointegracion.py) — ⚠️ sin referencias externas encontradas
> Script reusable: elasticidad-precio de demanda domestica por segmento, y
- `cargar_datos_ventas()` (L51)
- `construir_panel_elasticidad(fact, dim)` — Panel mensual por SKU, SOLO canales domesticos (excluye Exportacion (L57)
- `_extraer_stats(modelo, coef)` (L80)
- `correr_elasticidad(panel)` — Corre el modelo global y por segmento. Devuelve dict {segmento: stats}, (L90)
- `chequeo_sentido_economico(resultados)` — Compara beta de segmentos elasticos esperados (Entrada, Granel/Masivo) (L112)
- `guardar_resultados_elasticidad(resultados, observacion)` (L138)
- `correr_tarea_elasticidad()` (L145)
- `cargar_series_macro()` (L157)
- *...y 7 funciones más*

### [`cointegracion.py`](05_Analisis_Econometrico/src/cointegracion.py) — 🔗 conectado
> Test de cointegracion Engle-Granger de 2 pasos, con verificacion previa de
- `orden_integracion(serie, alpha)` — Devuelve 'I(0)' si la serie en niveles ya es estacionaria (ADF rechaza (L20)
- `test_engle_granger(serie_y, serie_x, alpha)` — Ejecuta ADF sobre ambas series primero (reporta orden de integracion), (L32)

### [`construir_curva_historica.py`](05_Analisis_Econometrico/src/construir_curva_historica.py) — ⚠️ sin referencias externas encontradas
> Construccion de la curva Rofex teorica HISTORICA (60 meses, 2021-01 a 2025-12)
- `_leer_serie_mensual(path)` — Lee un CSV de 2 columnas (date, value) a un dict {'YYYY-MM-DD': float}. (L54)
- `build_curva_historica(fx_csv, badlar_csv, tna_externa)` — Construye la curva Rofex teorica (forward a 90 dias via CIP) para cada (L66)
- `guardar_csv(filas, output_csv)` (L102)
- `_correlacion(xs, ys)` (L120)
- `imprimir_resumen(filas)` (L129)

### [`elasticidad.py`](05_Analisis_Econometrico/src/elasticidad.py) — 🔗 conectado
> Elasticidad precio-demanda via regresion log-log con efectos fijos de
- `estimar_elasticidad(panel, log_vol_col, log_precio_col, sku_col, mes_col)` — panel: DataFrame con una fila por SKU x periodo. Debe contener columnas (L18)
- `elasticidad_por_segmento(panel, segmento_col)` — Corre la regresion por separado para cada segmento (Entrada/Reserva/Icono/etc) (L31)

### [`estacionalidad_y_forecast.py`](05_Analisis_Econometrico/src/estacionalidad_y_forecast.py) — ⚠️ sin referencias externas encontradas
> Estacionalidad (STL) y forecasting (SARIMA) sobre la demanda domestica agregada
- `construir_serie_mensual_domestica(fact_ventas_path, canal_excluido)` — Agrega Ventas.csv por mes calendario (sum(VolumenReal)), (L44)
- `comparar_con_indice_real(indice_recuperado, indice_real_path)` — Compara el indice estacional recuperado por STL contra el indice real de (L73)
- `ejecutar_tarea1_estacionalidad(fact_ventas_path, indice_real_path, outputs_dir)` — Corre la Tarea 1 completa y persiste estacionalidad_resultados.json. (L114)
- `seleccionar_mejor_sarima(train, ordenes_no_estacionales, ordenes_estacionales, period)` — Grid chico sobre (p,d,q) x (P,D,Q,period); se queda con el de menor AIC en (L147)
- `calcular_mape_rmse(real, pred)` (L202)
- `ejecutar_tarea2_forecast(fact_ventas_path, outputs_dir, n_test)` — Corre la Tarea 2 completa (backtest SARIMA 12m) y persiste forecast_resultados.json. (L210)

### [`exportar_resultados_powerbi.py`](05_Analisis_Econometrico/src/exportar_resultados_powerbi.py) — ⚠️ sin referencias externas encontradas
> Exporta los resultados del motor econometrico (Analisis_Econometrico) como
- `exportar_elasticidad()` (L23)
- `exportar_estacionalidad()` (L41)
- `exportar_forecast()` (L48)
- `exportar_cointegracion()` (L82)
- `construir_curva_rofex_diaria_real()` — Reemplaza MercadoCambiario.csv (antes sine-wave) por CIP real (L96)

### [`fx_pricing.py`](05_Analisis_Econometrico/src/fx_pricing.py) — 🔗 conectado
> Paridad de tasas de interes cubierta (Covered Interest Rate Parity, CIP).
- **class `CIPResult`** (L21)
- `forward_teorico(spot, tna_domestica, tna_externa, dias)` — Precio forward teorico via CIP. Tasas en TNA (ej. 0.40 = 40% anual). (L30)
- `tna_implicita_de_forward(spot, forward, dias)` — Tasa implicita anualizada que resulta de un spot y un forward dados. (L37)
- `construir_curva(spot, tna_domestica, tna_externa)` — Construye el punto de la curva a 90 dias (el tenor usado en el modulo de (L44)

### [`inferencia_causal_erpt.py`](05_Analisis_Econometrico/src/inferencia_causal_erpt.py) — ⚠️ sin referencias externas encontradas
> Motor de Inferencia Causal & Pass-Through Cambiario (ERPT).
- `run_causal_inference_and_erpt()` (L26)

### [`ml_riesgo_prediccion.py`](05_Analisis_Econometrico/src/ml_riesgo_prediccion.py) — ⚠️ sin referencias externas encontradas
> Motor de Machine Learning: Riesgo Binario & Forecasting Supervisado sobre Series de Tiempo.
- `run_ml_risk_and_prediction()` (L27)

### [`modelo_miller_orr_var.py`](05_Analisis_Econometrico/src/modelo_miller_orr_var.py) — ⚠️ sin referencias externas encontradas
> Motor Cuantitativo de Tesoreria, Modelos Estocasticos y Stress Testing.
- `run_miller_orr_and_var()` (L23)

### [`seasonality.py`](05_Analisis_Econometrico/src/seasonality.py) — 🔗 conectado
> Descomposicion estacional real (STL) -- requiere series >= 24 meses (2 ciclos
- `descomponer_estacional(serie, periodo, robust)` — serie: pd.Series indexada por fecha mensual (DatetimeIndex, freq='MS'), sin NaN. (L12)

### [`audit_powerbi_suite.py`](tools/audit_powerbi_suite.py) — ⚠️ sin referencias externas encontradas
> Auditor Maestro de Calidad, Integridad y Cero Hardcodes para la Suite Power BI.
- `run_suite_audit()` (L28)

### [`generate_and_sync_icons.py`](tools/generate_and_sync_icons.py) — ⚠️ sin referencias externas encontradas
> Generador Maestro y Sincronizador de Iconos Ejecutivos UXBIA.
- `make_base()` (L30)
- `generate_new_icons()` (L49)
- `sync_all_icons_and_reports()` (L193)

### [`inject_kpi_icons.py`](tools/inject_kpi_icons.py) — ⚠️ sin referencias externas encontradas
> Inyector de Contenedores Visuales 'image' para Iconos de Tarjetas KPI en Fabric PBIR.
- `inject_icons()` (L116)

### [`update_matrices_with_rules.py`](tools/update_matrices_with_rules.py) — ⚠️ sin referencias externas encontradas
> Actualizador Maestro de Matrices Analiticas con Semaforos y Reglas de Decision Prescriptivas.
- `update_04_operaciones_matrices()` (L27)
- `update_03_comercial_matrices()` (L282)
- `update_02_controller_matrices()` (L392)
- `update_06_riesgo_matrices()` (L436)

