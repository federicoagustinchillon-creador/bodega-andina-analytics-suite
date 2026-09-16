# Compact AST Repository Map (Portfolio_Empresarial_PowerBI)
> **Propósito**: Mapa ultracompacto de símbolos, docstrings y conectividad para alimentar a agentes de IA con pocos tokens.
> **Directorios escaneados**: 00_Data_Engineering_ETL, 04_Econometric_Analysis, tools (14 módulos)
> **'conectado'** = referenciado (import o nombre de archivo) desde otro lugar del repo. 'sin referencias externas' no implica código roto -- puede ser un script standalone válido que nadie documentó todavía en SKILL_ROUTER.md.

### [`audit_suite03_operations.py`](00_Data_Engineering_ETL/audit_suite03_operations.py) — ⚠️ sin referencias externas encontradas
> Auditoria Integral de Modelado de Datos y TMDL para Suite 03 Operations
- `test_fact_operaciones_planta()` (L18)
- `test_fact_inventario_guarda()` (L38)
- `test_cuentas_contables_y_opex()` (L63)
- `test_semantic_model_tmdl()` (L87)
- `test_duckdb_integration()` (L128)

### [`etl_pipeline_cleaner.py`](00_Data_Engineering_ETL/etl_pipeline_cleaner.py) — ⚠️ sin referencias externas encontradas
> ===================================================================================
- `parse_date_robust(date_val)` — Parsea de forma robusta cadenas de fecha en diversos formatos a objeto datetime.date. (L33)
- `escanear_rango_fechas_observado(raw_dir)` — Recorre las fuentes transaccionales crudas (ventas, OPEX, remitos de planta, (L65)
- `clean_currency_or_number(val)` — Limpia cadenas numericas con simbolos monetarios, puntos de miles y comas decimales. (L99)
- `clean_string_col(series, case)` — Elimina espacios en blanco exteriores, multiples espacios interiores y ajusta mayusculas. (L122)
- `run_etl()` (L137)

### [`generar_datos_historicos_ventas.py`](00_Data_Engineering_ETL/generar_datos_historicos_ventas.py) — ⚠️ sin referencias externas encontradas
> Genera datos crudos (raw) de ventas 2021-2025 para 36 SKUs, calibrados contra
- `cargar_series_reales()` (L102)
- `sucio_fecha(fecha, i)` — Reproduce la mezcla de formatos de fecha del archivo raw original. (L111)
- `sucio_texto(v, i)` — Ensucia levemente MATNR/INCO1 (case + espacios) como el archivo original. (L118)
- `generar()` (L129)
- `generar_maestro_productos()` (L205)

### [`generar_presupuesto_2025.py`](00_Data_Engineering_ETL/generar_presupuesto_2025.py) — ⚠️ sin referencias externas encontradas
> Expande raw_presupuesto_horizontal.csv de 8 a 36 SKUs (catalogo actual),
- `cargar_catalogo()` (L30)
- `cargar_indice_estacional()` (L34)
- `generar()` (L39)

### [`update_data_layer.py`](00_Data_Engineering_ETL/update_data_layer.py) — ⚠️ sin referencias externas encontradas
> Script de Actualizacion de Capa de Datos y Modelos Semanticos
- `update_fact_operaciones_planta()` (L16)
- `create_fact_inventario_guarda()` (L51)
- `update_dim_cuentas_contables()` (L177)
- `update_fact_opex_mensual()` (L208)

### [`analisis_elasticidad_cointegracion.py`](04_Econometric_Analysis/src/analisis_elasticidad_cointegracion.py) — ⚠️ sin referencias externas encontradas
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

### [`cointegracion.py`](04_Econometric_Analysis/src/cointegracion.py) — 🔗 conectado
> Test de cointegracion Engle-Granger de 2 pasos, con verificacion previa de
- `orden_integracion(serie, alpha)` — Devuelve 'I(0)' si la serie en niveles ya es estacionaria (ADF rechaza (L20)
- `test_engle_granger(serie_y, serie_x, alpha)` — Ejecuta ADF sobre ambas series primero (reporta orden de integracion), (L32)

### [`construir_curva_historica.py`](04_Econometric_Analysis/src/construir_curva_historica.py) — ⚠️ sin referencias externas encontradas
> Construccion de la curva Rofex teorica HISTORICA (60 meses, 2021-01 a 2025-12)
- `_leer_serie_mensual(path)` — Lee un CSV de 2 columnas (date, value) a un dict {'YYYY-MM-DD': float}. (L54)
- `build_curva_historica(fx_csv, badlar_csv, tna_externa)` — Construye la curva Rofex teorica (forward a 90 dias via CIP) para cada (L66)
- `guardar_csv(filas, output_csv)` (L102)
- `_correlacion(xs, ys)` (L120)
- `imprimir_resumen(filas)` (L129)

### [`elasticidad.py`](04_Econometric_Analysis/src/elasticidad.py) — 🔗 conectado
> Elasticidad precio-demanda via regresion log-log con efectos fijos de
- `estimar_elasticidad(panel, log_vol_col, log_precio_col, sku_col, mes_col)` — panel: DataFrame con una fila por SKU x periodo. Debe contener columnas (L18)
- `elasticidad_por_segmento(panel, segmento_col)` — Corre la regresion por separado para cada segmento (Entrada/Reserva/Icono/etc) (L31)

### [`estacionalidad_y_forecast.py`](04_Econometric_Analysis/src/estacionalidad_y_forecast.py) — ⚠️ sin referencias externas encontradas
> Estacionalidad (STL) y forecasting (SARIMA) sobre la demanda domestica agregada
- `construir_serie_mensual_domestica(fact_ventas_path, canal_excluido)` — Agrega fact_ventas_reales.csv por mes calendario (sum(VolumenReal)), (L44)
- `comparar_con_indice_real(indice_recuperado, indice_real_path)` — Compara el indice estacional recuperado por STL contra el indice real de (L73)
- `ejecutar_tarea1_estacionalidad(fact_ventas_path, indice_real_path, outputs_dir)` — Corre la Tarea 1 completa y persiste estacionalidad_resultados.json. (L114)
- `seleccionar_mejor_sarima(train, ordenes_no_estacionales, ordenes_estacionales, period)` — Grid chico sobre (p,d,q) x (P,D,Q,period); se queda con el de menor AIC en (L147)
- `calcular_mape_rmse(real, pred)` (L202)
- `ejecutar_tarea2_forecast(fact_ventas_path, outputs_dir, n_test)` — Corre la Tarea 2 completa (backtest SARIMA 12m) y persiste forecast_resultados.json. (L210)

### [`exportar_resultados_powerbi.py`](04_Econometric_Analysis/src/exportar_resultados_powerbi.py) — ⚠️ sin referencias externas encontradas
> Exporta los resultados del motor econometrico (04_Econometric_Analysis) como
- `exportar_elasticidad()` (L23)
- `exportar_estacionalidad()` (L41)
- `exportar_forecast()` (L48)
- `exportar_cointegracion()` (L82)
- `construir_curva_rofex_diaria_real()` — Reemplaza fact_mercado_rofex_futuros.csv (antes sine-wave) por CIP real (L96)

### [`fx_pricing.py`](04_Econometric_Analysis/src/fx_pricing.py) — 🔗 conectado
> Paridad de tasas de interes cubierta (Covered Interest Rate Parity, CIP).
- **class `CIPResult`** (L21)
- `forward_teorico(spot, tna_domestica, tna_externa, dias)` — Precio forward teorico via CIP. Tasas en TNA (ej. 0.40 = 40% anual). (L30)
- `tna_implicita_de_forward(spot, forward, dias)` — Tasa implicita anualizada que resulta de un spot y un forward dados. (L37)
- `construir_curva(spot, tna_domestica, tna_externa)` — Construye el punto de la curva a 90 dias (el tenor usado en el modulo de (L44)

### [`seasonality.py`](04_Econometric_Analysis/src/seasonality.py) — 🔗 conectado
> Descomposicion estacional real (STL) -- requiere series >= 24 meses (2 ciclos
- `descomponer_estacional(serie, periodo, robust)` — serie: pd.Series indexada por fecha mensual (DatetimeIndex, freq='MS'), sin NaN. (L12)

### [`audit_powerbi_suite.py`](tools/audit_powerbi_suite.py) — ⚠️ sin referencias externas encontradas
> Auditor Maestro de Calidad, Integridad y Cero Hardcodes para la Suite Power BI.
- `run_suite_audit()` (L26)

