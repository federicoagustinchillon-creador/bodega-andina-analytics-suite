# Compact AST Repository Map (Portfolio_Empresarial_PowerBI)
> **Propósito**: Mapa ultracompacto de símbolos, docstrings y conectividad para alimentar a agentes de IA con pocos tokens.
> **Directorios escaneados**: 00_Data_Engineering_ETL, tools (4 módulos)
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

### [`update_data_layer.py`](00_Data_Engineering_ETL/update_data_layer.py) — ⚠️ sin referencias externas encontradas
> Script de Actualizacion de Capa de Datos y Modelos Semanticos
- `update_fact_operaciones_planta()` (L16)
- `create_fact_inventario_guarda()` (L51)
- `update_dim_cuentas_contables()` (L177)
- `update_fact_opex_mensual()` (L208)

### [`audit_powerbi_suite.py`](tools/audit_powerbi_suite.py) — ⚠️ sin referencias externas encontradas
> Auditor Maestro de Calidad, Integridad y Cero Hardcodes para la Suite Power BI.
- `run_suite_audit()` (L26)

