# 00_Data_Engineering_ETL · Bodega & Agroindustria Andina S.A.

## Ingesta de Datos, Pipeline Determinista de Limpieza, Curación y Modelado Relacional
**Autor:** Federico Agustín Chillón  
**Afiliación Académica:** Facultad de Ciencias Económicas — Universidad Nacional de Cuyo (UNCUYO)  
**Stack Tecnológico:** Python 3.12, Pandas, DuckDB, PostgreSQL DDL/Views, JSON Audit Reporting  
**Estándar de Calidad:** 100% Integridad Referencial · Cero Claves Huérfanas · Validación Determinista  

---

### 1. Visión General & Objetivos de Ingeniería de Datos

En entornos corporativos reales, los datos analíticos casi nunca provienen de tablas relacionales limpias. Por el contrario, los analistas y controllers deben lidiar con:
1. **Volcados crudos de ERP (SAP SD/MM):** Registros con códigos en mayúsculas/minúsculas mezcladas (`mal-res-750`), espacios espurios, formatos de fecha heterogéneos (`YYYY/MM/DD`, `DD-MM-YYYY`, `YYYYMMDD`) y valores nulos.
2. **Presupuestos Horizontales en Hojas de Cálculo:** Matrices desnormalizadas donde cada mes es una columna separada (`Ene_Vol`, `Feb_Vol`, ..., `Dic_Ing`), incompatibles con motores columnares modernos.
3. **Registros de Báscula y Remitos de Vendimia:** Datos ingresados manualmente en planta con discrepancias en nombres de fincas, variedades de uva y pesajes.
4. **Integridad Referencial Rota:** Transacciones con códigos de producto o centros de costo que no existen en las tablas maestras.

Esta capa **00_Data_Engineering_ETL** implementa un pipeline automatizado, auditable y de calidad de grado de producción que transforma estos insumos crudos en un **Esquema en Estrella (Star Schema)** completamente saneado y listo para ser consumido por los modelos semánticos de Power BI / Fabric.

---

### 2. Estructura de Directorios

```
00_Data_Engineering_ETL/
|-- raw/                             # Volcados crudos de SAP y planillas operativas
|   |-- raw_sap_vbrk_vbrp_ventas.csv
|   |-- raw_presupuesto_horizontal.csv
|   |-- raw_planta_molienda_remitos.csv
|   |-- raw_maestro_centros_costo.csv
|   |-- raw_maestro_productos.csv
|   \-- raw_balance_capital_trabajo.csv
|-- etl_pipeline_cleaner.py          # Script maestro de limpieza, unpivot y validación
|-- data_quality_report.json         # Certificado de auditoría con métricas cuantitativas
|-- sql/                             # Definición DDL y Vistas Analíticas
|   |-- 01_schema_ddl.sql
|   \-- 02_analytical_views.sql
\-- curated_gold/                    # Tablas dimensionales y de hechos curadas (CSV UTF-8)
    |-- dim_calendario.csv
    |-- dim_productos.csv
    |-- dim_centros_costo.csv
    |-- dim_cuentas_contables.csv
    |-- fact_ventas_reales.csv
    |-- fact_presupuesto_ventas.csv
    |-- fact_opex_mensual.csv
    |-- fact_capital_trabajo.csv
    \-- fact_operaciones_planta.csv
```

---

### 3. Pipeline de Limpieza & Algoritmos de Normalización (`etl_pipeline_cleaner.py`)

1. **Parseo Robusto de Fechas (`parse_date_robust`):** Evalúa heurísticamente 8 patrones de fecha comunes en sistemas legados y los normaliza al estándar ISO 8601 (`YYYY-MM-DD`) generando adicionalmente la clave entera `DateKey` (`YYYYMMDD`).
2. **Limpieza de Strings y Estandarización:** Función `clean_string_col` que elimina espacios redundantes (strip), colapsa espacios internos y homogeniza códigos identificadores a mayúsculas.
3. **Unpivot Dinámico de Presupuesto:** Transforma la estructura matricial de 24 columnas mensuales a un formato tidy columnar (`DateKey, ProductoID, CentroCostoID, VolumenPresupuestado, IngresosPresupuestados, CostoPresupuestado, MargenBrutoPresupuestado`), calculando márgenes unitarios de forma determinista.
4. **Aseguramiento de Integridad Referencial:** Compara cada clave foránea en las tablas de hechos (`ProductoID`, `CentroCostoID`, `CuentaID`, `DateKey`) contra el conjunto de claves primarias válidas de las dimensiones. Si se detecta una clave huérfana, el pipeline la resuelve y registra en el log de auditoría.
5. **Categorización ABC Automatizada:** Clasifica las líneas de vino (`Alta Gama`, `Granel / Masivo`, `Espumantes`, `Entrada / Volumen`) en clases estratégicas A, B y C directamente en la dimensión maestra.

---

### 4. Certificación de Calidad de Datos (`data_quality_report.json`)

El script genera automáticamente un reporte en JSON con la auditoría de cada ejecución:
- **Registros Procesados:** >2.500 registros a través de 9 tablas.
- **Inconsistencias Corregidas:** Strings mal formateados, fechas parseadas y números casteados.
- **Claves Huérfanas:** 0 claves huérfanas residuales.
- **Tasa de Validez Global:** **100.00%**.

---

### 5. Modelado SQL Relacional (`sql/`)

- `01_schema_ddl.sql`: Esquema DDL formal con llaves primarias (`PRIMARY KEY`), foráneas (`FOREIGN KEY`), restricciones de no nulidad (`NOT NULL`) y chequeos de rango (`CHECK constraints`), compatible tanto con **PostgreSQL** como con **DuckDB**.
- `02_analytical_views.sql`: Vistas de negocio optimizadas para reporting SQL directo (P&L Cascada, Pareto Comercial y Eficiencia Enológica de Vendimia).
