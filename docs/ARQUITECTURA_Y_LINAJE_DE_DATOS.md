# Arquitectura y Linaje de Datos — Portfolio Empresarial Power BI

**Repo:** `Portfolio_Empresarial_PowerBI` · **Autor:** Federico Agustín Chillón (UNCUYO) · **Empresa ficticia:** Bodega & Agroindustria Andina S.A.

---

## 1. Visión General de Arquitectura

Este portfolio simula la stack analítica completa de una bodega exportadora argentina: desde el dato crudo (volcados ERP-like, planillas de planta) hasta 4 modelos semánticos de Power BI en producción, pasando por una capa de ingeniería de datos (ETL determinista) y una capa de econometría/ML aplicada en Python. La decisión de **separar en 4 proyectos PBIP independientes** — `02_Control_de_Gestion`, `03_Inteligencia_Comercial`, `04_Operaciones_y_Planta`, `06_Modelos_de_Riesgo_y_Prediccion` — en lugar de un único modelo monolítico replica cómo se organizan los equipos de BI en una empresa real: Finanzas, Comercial, Operaciones y Riesgo/Data Science tienen dueños, cadencias de refresh y audiencias ejecutivas distintas, aunque comparten la misma capa `curated_gold` como fuente única de verdad (single source of truth). La capa `Analisis_Econometrico` (carpeta real `05_Analisis_Econometrico`) es una quinta pieza, no un modelo semántico sino un motor de análisis cuantitativo en Python (elasticidad-precio, cointegración, estacionalidad STL, forecasting SARIMA, pricing de futuros vía CIP, y desde esta actualización también ML de riesgo/forecasting, inferencia causal y stress testing financiero) cuyos resultados se vuelcan de regreso a `curated_gold` y de ahí se consumen dentro de `03_Inteligencia_Comercial` y, para los 3 scripts nuevos, dentro de `06_Modelos_de_Riesgo_y_Prediccion` (y parcialmente `02_Control_de_Gestion`, ver §3).

La filosofía de datos del repo es **"sintético pero calibrado, no inventado sin ancla"**: los datos transaccionales (ventas, presupuesto, OPEX, operaciones de planta) se generan con `numpy` para tener volumen y variedad de un dataset real de producción, pero cada generador ancla sus parámetros (estacionalidad, tipo de cambio, inflación, elasticidad esperada por segmento) contra series **reales** publicadas por BCRA (tipo de cambio A3500, tasa BADLAR), INDEC (IPC) y el INV (índice estacional de consumo de vino, mercado interno 2024). Esto es lo que permite que los tests econométricos (cointegración precio-IPC, pass-through cambiario, elasticidad por segmento) tengan contenido económico genuino en vez de ser ejercicios triviales sobre ruido aleatorio.

**`06_Modelos_de_Riesgo_y_Prediccion`** es el componente más reciente y el cuarto modelo semántico PBIP: aplica machine learning supervisado y métodos cuantitativos de riesgo financiero sobre la misma capa `curated_gold`, en 4 páginas — `p1_clasif` (clasificación/scoring de riesgo crediticio con Regresión Logística L2, Random Forest y Gradient Boosting, evaluados por curva ROC/AUC), `p2_forecast` (forecasting de demanda con Gradient Boosting Regressor vs. benchmark SARIMAX), `p3_stress` (VaR/CVaR vía Monte Carlo, modelo de tesorería de Miller-Orr, reverse stress testing) y `p4_causal` (Double Machine Learning para el efecto causal (ATE) de descuentos comerciales, y pass-through cambiario/ERPT). A diferencia de `03_Inteligencia_Comercial` (econometría clásica: regresión log-log, Engle-Granger, STL/SARIMA), `06` está construido sobre `scikit-learn` y `scipy.stats`; sus 3 scripts fuente (`ml_riesgo_prediccion.py`, `inferencia_causal_erpt.py`, `modelo_miller_orr_var.py`) viven junto a los 5 scripts econométricos preexistentes en `05_Analisis_Econometrico/src/`.

---

## 2. Diagrama de Linaje de Datos

```mermaid
flowchart TB
    subgraph REAL["Fuentes reales (BCRA / INDEC / INV)"]
        R1["BCRA — Tipo de Cambio A3500<br/>bcra_tipo_cambio.csv"]
        R2["BCRA — Tasa BADLAR<br/>badlar_p1.json / badlar_p2.json"]
        R3["INDEC — IPC Nacional Mensual<br/>ipc_mensual_2021_2025.csv"]
        R4["INV — Índice Estacional Consumo Vino 2024<br/>indice_estacional_inv_2024.csv"]
    end

    subgraph GEN["Scripts generadores (01_Limpieza_de_Datos, numpy calibrado)"]
        G1["generar_datos_historicos_ventas.py<br/>(SAP-like ventas + maestro productos)"]
        G2["generar_presupuesto_2025.py<br/>(presupuesto horizontal 36 SKU)"]
        G3["Archivos raw estáticos<br/>(OPEX, centros de costo, planta,<br/>capital de trabajo, plan de cuentas)"]
    end

    subgraph RAW["01_Limpieza_de_Datos/raw/"]
        RW1[raw_sap_vbrk_vbrp_ventas.csv]
        RW2[raw_maestro_productos.csv]
        RW3[raw_presupuesto_horizontal.csv]
        RW4[raw_gastos_opex.csv]
        RW5[raw_maestro_centros_costo.csv]
        RW6[raw_planta_molienda_remitos.csv]
        RW7[raw_balance_capital_trabajo.csv]
        RW8[raw_plan_cuentas_contables.csv]
    end

    ETL["etl_pipeline_cleaner.py<br/>(parseo fechas, limpieza strings,<br/>unpivot presupuesto, integridad referencial)"]
    UPD["update_data_layer.py<br/>(geolocalización planta, InventarioGuarda,<br/>cuentas industriales, redistribución OPEX fabril)"]

    subgraph GOLD["01_Limpieza_de_Datos/curated_gold/ (single source of truth)"]
        GD1[Productos.csv]
        GD2[CentrosCosto.csv]
        GD3[PlanCuentas.csv]
        GD4[Calendario.csv]
        GD5[Ventas.csv]
        GD6[PresupuestoVentas.csv]
        GD7[GastosOperativos.csv]
        GD8[CapitalTrabajo.csv]
        GD9[ProduccionPlanta.csv]
        GD10[InventarioGuarda.csv]
        GD11["MercadoCambiario.csv<br/>(CIP real, no sine-wave)"]
        GD12["ElasticidadSegmento.csv<br/>EstacionalidadMensual.csv<br/>PronosticoDemanda.csv / _metadata.csv<br/>TestsCointegracion.csv"]
        GD13["ML_Curva_ROC.csv / ML_Metricas_Clasificacion.csv<br/>ML_Matriz_Confusion.csv / ML_Scoring_Riesgo.csv"]
        GD14["ML_Metricas_Forecasting.csv<br/>ML_Forecasting_Comparativo.csv"]
        GD15["Inferencia_Causal_Resultados.csv<br/>Inferencia_Causal_Detalle_Segmento.csv"]
        GD16["Tesoreria_Miller_Orr_Diario.csv<br/>Tesoreria_Parametros_Optimos.csv"]
        GD17["Riesgo_Stress_Testing_VaR.csv<br/>Riesgo_Distribucion_MonteCarlo_30d.csv<br/>Riesgo_Reverse_Stress_Testing.csv"]
    end

    subgraph ECON["Analisis_Econometrico (rama paralela Python)"]
        E1["elasticidad.py + analisis_elasticidad_cointegracion.py<br/>(regresión log-log por segmento)"]
        E2["cointegracion.py<br/>(Engle-Granger 2 pasos, pass-through)"]
        E3["estacionalidad_y_forecast.py<br/>(STL + SARIMA grid search)"]
        E4["fx_pricing.py + construir_curva_historica.py<br/>(CIP: forward teórico ARS/USD)"]
        E5["exportar_resultados_powerbi.py<br/>(vuelca outputs/*.json a curated_gold)"]
        E6["ml_riesgo_prediccion.py<br/>(Regresion Logistica L2, Random Forest,<br/>Gradient Boosting — ROC/AUC, matriz confusion,<br/>scoring; GBDT vs SARIMAX forecast demanda)"]
        E7["inferencia_causal_erpt.py<br/>(Double Machine Learning ATE descuentos,<br/>Exchange Rate Pass-Through insumos/FOB/domestico)"]
        E8["modelo_miller_orr_var.py<br/>(Miller-Orr tenencia optima efectivo,<br/>Monte Carlo CF-VaR/CVaR, reverse stress testing)"]
    end

    subgraph SM01["Control_de_Gestion.SemanticModel"]
        S01T["Productos, CentrosCosto, PlanCuentas,<br/>Calendario, DesgloseCascada (DAX calc.)<br/>Ventas, PresupuestoVentas,<br/>GastosOperativos, CapitalTrabajo,<br/>MercadoCambiario, CobranzasExportacion"]
    end

    subgraph SM02["Inteligencia_Comercial.SemanticModel"]
        S02T["Productos (+CategoriaABC DAX),<br/>CentrosCosto, Calendario<br/>Ventas, PresupuestoVentas,<br/>ElasticidadSegmento, EstacionalidadMensual,<br/>PronosticoDemanda, PrecisionModelo,<br/>TestsCointegracion"]
    end

    subgraph SM03["Operaciones_y_Planta.SemanticModel"]
        S03T["Productos, CentrosCosto, PlanCuentas,<br/>Calendario<br/>ProduccionPlanta, GastosOperativos,<br/>CapitalTrabajo, InventarioGuarda"]
    end

    subgraph SM06["06_Riesgo.SemanticModel"]
        S06T["Productos, Calendario<br/>ML_Curva_ROC, ML_Metricas_Clasificacion,<br/>ML_Matriz_Confusion, ML_Scoring_Riesgo,<br/>ML_Metricas_Forecasting, ML_Forecasting_Comparativo,<br/>Inferencia_Causal_Resultados,<br/>Inferencia_Causal_Detalle_Segmento,<br/>Riesgo_Stress_Testing_VaR,<br/>Riesgo_Distribucion_MonteCarlo_30d,<br/>Riesgo_Reverse_Stress_Testing"]
    end

    R1 --> G1
    R3 --> G1
    R4 --> G1
    R1 --> G2
    R4 --> G2

    G1 --> RW1
    G1 --> RW2
    G2 --> RW3
    G3 --> RW4
    G3 --> RW5
    G3 --> RW6
    G3 --> RW7
    G3 --> RW8

    RW1 --> ETL
    RW2 --> ETL
    RW3 --> ETL
    RW4 --> ETL
    RW5 --> ETL
    RW6 --> ETL
    RW7 --> ETL
    RW8 --> ETL

    ETL --> GD1
    ETL --> GD2
    ETL --> GD3
    ETL --> GD4
    ETL --> GD5
    ETL --> GD6
    ETL --> GD7
    ETL --> GD8
    ETL --> GD9

    GD9 --> UPD
    GD3 --> UPD
    GD7 --> UPD
    UPD --> GD9
    UPD --> GD10
    UPD --> GD3
    UPD --> GD7

    GD5 --> E1
    GD1 --> E1
    R3 --> E1
    R1 --> E2
    R1 --> E3
    R4 --> E3
    R1 --> E4
    R2 --> E4
    E1 --> E5
    E2 --> E5
    E3 --> E5
    E4 --> E5
    E5 --> GD11
    E5 --> GD12

    GD5 --> E6
    E6 --> GD13
    E6 --> GD14

    GD5 --> E7
    GD4 --> E7
    E7 --> GD15

    GD11 --> E8
    E8 --> GD16
    E8 --> GD17

    GD1 --> SM01
    GD2 --> SM01
    GD3 --> SM01
    GD4 --> SM01
    GD5 --> SM01
    GD6 --> SM01
    GD7 --> SM01
    GD8 --> SM01
    GD11 --> SM01
    GD16 --> SM01

    GD1 --> SM02
    GD2 --> SM02
    GD4 --> SM02
    GD5 --> SM02
    GD6 --> SM02
    GD12 --> SM02

    GD1 --> SM03
    GD2 --> SM03
    GD3 --> SM03
    GD4 --> SM03
    GD9 --> SM03
    GD7 --> SM03
    GD8 --> SM03
    GD10 --> SM03

    GD1 --> SM06
    GD4 --> SM06
    GD13 --> SM06
    GD14 --> SM06
    GD15 --> SM06
    GD17 --> SM06
```

**Nota de lectura:** `CobranzasExportacion.csv` (consumida solo por 01) vive en `curated_gold` sin un script generador identificado en el repo — ver la nota correspondiente en la tabla de linaje (§3). `DesgloseCascada` no tiene CSV en `curated_gold`: es una tabla 100% calculada en DAX (`partition ... = calculated`) dentro de `02_Control_de_Gestion`, usada para la cascada de EV/EP/EC en la página `p1_cascada`. `Tesoreria_Miller_Orr_Diario.csv` y `Tesoreria_Parametros_Optimos.csv` (`GD16`) los genera `modelo_miller_orr_var.py` junto con las tablas de riesgo de `06`, pero **las consume `02_Control_de_Gestion`** (tablas `TesoreriaMillerOrr`/`TesoreriaParametros`, folder `03 Optimo de Caja Miller-Orr` de `_Medidas_Tesoreria.tmdl`), no `06` — el nombre de tabla difiere del nombre del CSV en este caso, a diferencia del resto del repo donde coinciden.

---

## 3. Tabla de Linaje por Tabla `curated_gold`

**Nota de numeración:** en esta tabla, `01`/`02`/`03` refieren respectivamente a `02_Control_de_Gestion`, `03_Inteligencia_Comercial` y `04_Operaciones_y_Planta` (el orden en que se listaron en §1, no el prefijo de carpeta). Las filas nuevas de `06_Modelos_de_Riesgo_y_Prediccion` usan directamente el prefijo real `06` para no sumar un cuarto número ambiguo a esa convención.

| Tabla | Script que la genera | Modelo(s) semántico(s) que la consumen | Calibrado contra (fuente real) |
|---|---|---|---|
| `Productos.csv` | `etl_pipeline_cleaner.py` (desde `raw_maestro_productos.csv`, generado por `generar_datos_historicos_ventas.py::generar_maestro_productos()`) | 01, 02, 03 | — (maestro de producto; `CategoriaABC` NO se calcula acá, ver §5) |
| `CentrosCosto.csv` | `etl_pipeline_cleaner.py` (desde `raw_maestro_centros_costo.csv`, archivo raw estático) | 01, 02, 03 | — |
| `PlanCuentas.csv` | `etl_pipeline_cleaner.py` (desde `raw_plan_cuentas_contables.csv`) + `update_data_layer.py::update_dim_cuentas_contables()` (agrega 4 cuentas industriales CTA-201/202/203/204) | 01, 03 | — |
| `Calendario.csv` | `etl_pipeline_cleaner.py` (rango dinámico, no hardcodeado a un año fiscal fijo) | 01, 02, 03 | — |
| `Ventas.csv` | `etl_pipeline_cleaner.py` (desde `raw_sap_vbrk_vbrp_ventas.csv`, generado por `generar_datos_historicos_ventas.py`) | 01, 02 | IPC INDEC (deriva de precio doméstico), FX BCRA (precio exportación FOB→ARS), índice INV (estacionalidad de volumen) |
| `PresupuestoVentas.csv` | `etl_pipeline_cleaner.py` (unpivot de `raw_presupuesto_horizontal.csv`, generado por `generar_presupuesto_2025.py`) | 01, 02 | índice estacional INV (para expandir el presupuesto anual a mensual) |
| `GastosOperativos.csv` | `etl_pipeline_cleaner.py` (desde `raw_gastos_opex.csv`) + `update_data_layer.py::update_fact_opex_mensual()` (redistribuye OPEX fabril CC-101/102/103 en 4 cuentas industriales, con cuadratura exacta verificada por `assert`) | 01, 03 | — |
| `CapitalTrabajo.csv` | `etl_pipeline_cleaner.py` (desde `raw_balance_capital_trabajo.csv`) | 01, 03 | — |
| `ProduccionPlanta.csv` | `etl_pipeline_cleaner.py` (desde `raw_planta_molienda_remitos.csv`) + `update_data_layer.py::update_fact_operaciones_planta()` (agrega `Latitud`/`Longitud`/`UbicacionGeografica` por finca, coordenadas reales de Mendoza) | 03 | Coordenadas geográficas reales (Agrelo, Barrancas, Gualtallary, Altamira) |
| `InventarioGuarda.csv` | `update_data_layer.py::create_fact_inventario_guarda()` (síntesis directa, sin raw intermedio; semilla `np.random.seed(42)`, 12 meses × 5 SKU × 4 tipos de vasija) | 03 | Estacionalidad de vendimia/crianza modelada por lógica de negocio (no serie externa) |
| `MercadoCambiario.csv` | `exportar_resultados_powerbi.py::construir_curva_rofex_diaria_real()` (reemplazó una curva sine-wave sin sentido económico) | 01 (Tesorería), 02 (medida `Spot ARS/USD Serie`) | BCRA A3500 (spot diario) + BADLAR (tasa doméstica), vía CIP (`fx_pricing.py`) |
| `CobranzasExportacion.csv` | Sin script generador identificado en el repo (archivo estático en `curated_gold`) | 01 (Tesorería, página `p4_tesoreria`) | — |
| `ElasticidadSegmento.csv` | `exportar_resultados_powerbi.py::exportar_elasticidad()` (desde `outputs/elasticidad_resultados.json`, producido por `analisis_elasticidad_cointegracion.py` + `elasticidad.py`) | 02 (página `p4_econometria`) | IPC INDEC (deflactor implícito vía panel de precios) |
| `EstacionalidadMensual.csv` | `exportar_resultados_powerbi.py::exportar_estacionalidad()` (desde `estacionalidad_resultados.json`, producido por `estacionalidad_y_forecast.py`, descomposición STL vía `seasonality.py`) | 02 | Índice estacional real INV 2024 (columna `indice_estacional_real_inv2024` comparada contra STL recuperado) |
| `PronosticoDemanda.csv` / `PrecisionModelo.csv` | `exportar_resultados_powerbi.py::exportar_forecast()` (backtest SARIMA 12 meses, grid search AIC) | 02 | — (backtest sobre `Ventas`) |
| `TestsCointegracion.csv` | `exportar_resultados_powerbi.py::exportar_cointegracion()` (test Engle-Granger de 2 pasos vía `cointegracion.py`) | 02 | IPC INDEC (pass-through inflacionario) y FX BCRA (pass-through cambiario) |
| `ML_Curva_ROC.csv` | `ml_riesgo_prediccion.py::run_ml_risk_and_prediction()` (TPR/FPR por threshold, para las 3 curvas ROC de Regresión Logística L2, Random Forest y Gradient Boosting) | 06 | — (target de riesgo sintético vía log-odds estructural: plazo, mora histórica, variación de volumen, concentración, canal; ver §5) |
| `ML_Metricas_Clasificacion.csv` | `ml_riesgo_prediccion.py` (AUC-ROC, Accuracy, Recall, Precision, F1, threshold óptimo de Youden J, Brier Score, Log Loss — una fila por modelo) | 06 | — |
| `ML_Matriz_Confusion.csv` | `ml_riesgo_prediccion.py` (matriz de confusión **solo del modelo campeón por mayor AUC-ROC, por diseño** — ver §5 y el test `test_ml_matriz_confusion_es_del_modelo_ganador`) | 06 | — |
| `ML_Scoring_Riesgo.csv` | `ml_riesgo_prediccion.py` (score 0-100, nivel y prescripción de riesgo por cliente, sobre 350 clientes sintéticos con `np.random.seed(42)`) | 06 | — |
| `ML_Metricas_Forecasting.csv` | `ml_riesgo_prediccion.py` (segunda mitad del script: RMSE, MAE, MAPE, R² y % de reducción de error del Gradient Boosting Regressor vs. benchmark SARIMAX) | 06 | — (backtest sobre `Ventas`) |
| `ML_Forecasting_Comparativo.csv` | `ml_riesgo_prediccion.py` (forecast mensual GBDT / Random Forest / SARIMAX + intervalo de confianza 95%, con features de lags, medias móviles y armónicos de Fourier) | 06 | — |
| `Inferencia_Causal_Resultados.csv` | `inferencia_causal_erpt.py::run_causal_inference_and_erpt()` (ATE de descuentos comerciales vía Double Machine Learning — Chernozhukov 2018 — + ERPT a insumos secos, FOB y precios domésticos) | 06 | — (`true_ate` estructural fijado en el generador para poder verificar que el DML lo recupera pese a los confounders; ver §5) |
| `Inferencia_Causal_Detalle_Segmento.csv` | `inferencia_causal_erpt.py` (ATE causal y clasificación de elasticidad por 4 segmentos: Icono/Gran Reserva, Reserva/Roble, Varietales/Entrada, Bag in Box/Granel) | 06 | — |
| `Riesgo_Stress_Testing_VaR.csv` | `modelo_miller_orr_var.py::run_miller_orr_and_var()` (CF-VaR 95%/99% y CVaR a 30/60/90 días, Monte Carlo de 10.000 senderos con distribución t de Student ajustada) | 06 | Flujos derivados de `MercadoCambiario` (BCRA A3500 + BADLAR, ver fila de arriba) |
| `Riesgo_Distribucion_MonteCarlo_30d.csv` | `modelo_miller_orr_var.py` (distribución completa de cuantiles del horizonte 30 días, para el histograma de la página `p3_stress`) | 06 | ídem |
| `Riesgo_Reverse_Stress_Testing.csv` | `modelo_miller_orr_var.py` (4 escenarios metodología EBA/Basilea III, desde el escenario base hasta el "Reverse Stress Breakpoint" de insolvencia operativa crítica) | 06 | — (escenarios definidos por diseño en el script, no leídos de un CSV externo) |
| `Tesoreria_Miller_Orr_Diario.csv` | `modelo_miller_orr_var.py` (calibración diaria del modelo de Miller-Orr 1966: banda inferior `L`, punto de retorno `Z`, banda superior `H`, saldo ocioso, costo de oportunidad) | 01 (tablas `TesoreriaMillerOrr`/`TesoreriaParametros`, no `06` — ver nota de lectura en §2) | Tasa LECAP real (`TasaLecapReferenciaTNA` de `MercadoCambiario`) |
| `Tesoreria_Parametros_Optimos.csv` | `modelo_miller_orr_var.py` (8 parámetros óptimos del modelo: `L`, `Z`, `H`, saldo promedio esperado, varianza y desvío diario, TNA de costo de oportunidad, costo de transacción fijo) | 01 | ídem |

---

## 4. Catálogo de Medidas DAX Críticas por Dominio

Selección de medidas de negocio real (excluye auxiliares de formateo puro de tooltip/storytelling salvo que sean el mecanismo central de una página). Fuente: `_Medidas_*.tmdl` de cada `.SemanticModel/definition/tables/`, agrupadas por su `displayFolder`.

### 02_Control_de_Gestion — `_Medidas_Controller.tmdl`

| Medida | displayFolder | Qué mide | Fórmula (resumida) |
|---|---|---|---|
| `Desvio Ingresos %` | 01 Ingresos y Volumen | Desvío % de ingresos reales vs. presupuesto | `DIVIDE([Desvio Ingresos], [Ingresos Presupuesto], 0)` |
| `Margen Bruto % Real` | 02 Costos y Margen Bruto | Margen bruto real como % de ingresos | `DIVIDE([Margen Bruto Real], [Ingresos Reales], 0)` |
| `Efecto Volumen (EV)` / `Efecto Precio (EP)` / `Efecto Costo (EC)` | 03 Variance Analysis (Desvios) | Descomposición del desvío de margen bruto en 3 efectos independientes (análisis de variance clásico de controller) | fórmulas multilínea VAR/RETURN; se verifican con `Verificacion Desvio Cuadrado` |
| `Estado Cuadratura` | 03 Variance Analysis (Desvios) | Gate de integridad: confirma que EV+EP+EC cuadra exacto contra el desvío total | `IF(ROUND([Verificacion Desvio Cuadrado],2)=0, "CUADRATURA EXACTA ($0.00)", "DESCUADRE DETECTADO")` |
| `EBITDA Real` | 04 OPEX y EBITDA (SAP CO) | EBITDA real (margen bruto menos OPEX) | `[Margen Bruto Real] - [OPEX Real]` |
| `Alerta Semaforo OPEX` / `Color Semaforo OPEX` | 04 OPEX y EBITDA (SAP CO) | Semáforo de desvío OPEX vs. presupuesto para KPI cards | multi-línea, umbrales sobre `Desvio Ratio OPEX Puntos` |
| `Ciclo Conversion Efectivo (CCC)` | 05 Capital de Trabajo y Liquidez | Cash Conversion Cycle | `[DIO Promedio] + [DSO Promedio] - [DPO Promedio]` |
| `NOF Total` | 05 Capital de Trabajo y Liquidez | Necesidad Operativa de Fondos | `[Cuentas por Cobrar Total] + [Inventario Total] - [Cuentas por Pagar Total]` |
| `Cascada Desglose Valor` | 06 Flujo de Fondos y Creacion de Valor | Tabla base para el waterfall de creación de valor (alimenta `DesgloseCascada` calculada) | multi-línea |

### 02_Control_de_Gestion — `_Medidas_Tesoreria.tmdl`

| Medida | displayFolder | Qué mide | Fórmula (resumida) |
|---|---|---|---|
| `TNA Implicita Rofex 3M` | 01 Tesoreria y Cobertura Cambiaria | Tasa implícita anualizada del futuro Rofex 3M vs. spot, vía CIP | multi-línea, usa `MercadoCambiario` |
| `Spread Arbitraje bps` | 01 Tesoreria y Cobertura Cambiaria | Spread entre tasa implícita Rofex y benchmark LECAP, en puntos básicos | `([TNA Implicita Rofex 3M] - [TNA Benchmark LECAP]) * 10000` |
| `Recomendacion Cobertura` | 01 Tesoreria y Cobertura Cambiaria | Texto de recomendación de cobertura cambiaria basado en el spread | `SWITCH`/`IF` multi-línea |
| `Cobranzas USD Pendientes` | 02 Cobranzas de Exportacion USD | Exposición FOB en USD aún no cobrada, a la fecha de referencia | `CALCULATE(SUM(CobranzasExportacion[ImporteFOB_USD]), FechaCobroEstimada > [Fecha Referencia Simulada])` |
| `Exposicion Cambiaria Neta ARS` | 01 Tesoreria y Cobertura Cambiaria | Exposición neta en pesos, aplicando spot actual | `[Exposicion Cambiaria Neta USD] * [Spot ARS/USD Actual]` |

### 03_Inteligencia_Comercial — `_Medidas_Comercial.tmdl`

| Medida | displayFolder | Qué mide | Fórmula (resumida) |
|---|---|---|---|
| `Cumplimiento Presupuesto %` | 01 Ventas y Cumplimiento | % de cumplimiento de ingresos reales vs. presupuesto | `DIVIDE([Ingresos Reales], [Ingresos Presupuesto], 0)` |
| `Descuento Comercial Promedio %` | 02 Precios, Costos y Margen | Descuento efectivo promedio vs. precio de lista presupuestado | `DIVIDE([Precio Lista Presupuestado]-[Precio Promedio Real], [Precio Lista Presupuestado], 0)` |
| `Ventas Acumuladas %` | 03 Pareto y Cartera ABC | % acumulado de ingresos reales por SKU ordenado descendente (curva de Pareto) | `SUMX(FILTER(ALL/ALLSELECTED...))` multi-línea |
| `Clasificacion ABC` | 03 Pareto y Cartera ABC | Clase A/B/C real por SKU según % acumulado de ingresos (umbrales 75%/92%) | `IF([Ventas Acumuladas %]<=0.75,"Clase A", IF(<=0.92,"Clase B","Clase C"))` — ver §5, misma metodología que la columna calculada `CategoriaABC` de `Productos` |
| `Recomendacion Estrategica ABC` | 03 Pareto y Cartera ABC | Texto de acción comercial según clase ABC | `SWITCH([Clasificacion ABC], ...)` |
| `Deducciones Comerciales %` | 04 Elasticidad y Deducciones | Deducciones comerciales (bonificaciones, descuentos) como % de la facturación bruta | `DIVIDE([Deducciones Comerciales Total],[Facturacion Bruta Total],0)` |
| `Diagnostico Causal` | 06 Diagnostico Causal | Texto explicativo de la causa raíz dominante de un desvío de KPI | multi-línea, usa `Top Causa Desvio` + `Magnitud Desvio Top Causa` |

### 03_Inteligencia_Comercial — `_Medidas_Econometria.tmdl`

| Medida | displayFolder | Qué mide | Fórmula (resumida) |
|---|---|---|---|
| `MAPE Forecast` / `RMSE Forecast` | 01 Forecast | Error porcentual/cuadrático medio del backtest SARIMA 12 meses | `SELECTEDVALUE(PrecisionModelo[MAPE/RMSE])` |
| `Correlacion Estacional Real` | 02 Estacionalidad | Correlación entre el índice STL recuperado y el índice real INV 2024 | multi-línea |
| `Beta Elasticidad Icono` | 03 Elasticidad | Coeficiente de elasticidad-precio del segmento Gran Reserva / Icono | multi-línea, lee `ElasticidadSegmento` |
| `Cointegracion Tests Validos` | 04 Cointegracion | Cantidad de tests Engle-Granger que confirman cointegración (pass-through real) | multi-línea, lee `TestsCointegracion[EsValido]` |

### 04_Operaciones_y_Planta — `_Medidas_Operaciones.tmdl`

| Medida | displayFolder | Qué mide | Fórmula (resumida) |
|---|---|---|---|
| `Rendimiento Medio Extraccion %` | 01 Eficiencia y Recepcion Vendimia | Litros de mosto obtenidos por kilo de uva (eficiencia enológica) | `DIVIDE([Total Litros Mosto],[Total Kilos Uva],0)` |
| `Capacidad Maxima Molienda Semanal` | 01 Eficiencia y Recepcion Vendimia | Kilos de uva procesados equivalentes a capacidad semanal máxima de planta | `DIVIDE([Total Kilos Uva], 9.088, 0)` |
| `Desvio Fabril %` | 02 Costos Fabriles y Absorcion | Desvío % del costo fabril total (CC-101/102/103) vs. presupuesto | `DIVIDE([Desvio Fabril Total],[Costo Presupuesto Fabril],0)` |
| `Costo Unitario Real por Botella` | 02 Costos Fabriles y Absorcion | Costo fabril absorbido por botella equivalente producida | `DIVIDE([Costo Total Fabril],[Total Botellas Equivalentes],0)` |
| `Tasa Merma Crianza %` | 03 Inventario Guarda y Mermas | Merma promedio de volumen durante la guarda (barricas/piletas/estiba) | `AVERAGE(InventarioGuarda[MermaPct])` |
| `DIO Rango Optimo` / `DIO Desvio Exceso` | 03 Inventario Guarda y Mermas | Evalúa si los Días de Inventario en Guarda están dentro del rango óptimo esperado por tipo de vasija | multi-línea |
| `Diagnostico Causal` | 05 Diagnostico Causal | Causa raíz dominante del desvío de costo fabril (mismo patrón que en 02) | multi-línea |

### 06_Modelos_de_Riesgo_y_Prediccion — `_Medidas_Riesgo_Prediccion.tmdl`

70 medidas en total, agrupadas en 4 `displayFolder`. Muestra representativa por folder:

| Medida | displayFolder | Qué mide | Fórmula (resumida) |
|---|---|---|---|
| `AUC ROC Maximo Ganador` / `Modelo Clasificacion Ganador` | 01 Clasificacion y Scoring Crediticio | AUC-ROC máximo entre los 3 modelos y cuál es el modelo campeón | `CALCULATE(MAX(ML_Metricas_Clasificacion[AUC_ROC]))`; `FIRSTNONBLANK` filtrado por ese máximo |
| `Accuracy Ganador %` / `Recall Ganador %` / `Precision Ganador %` / `F1 Score Ganador` | 01 Clasificacion y Scoring Crediticio | Métricas de clasificación del modelo campeón (no de los 3) | `CALCULATE(MAX(ML_Metricas_Clasificacion[...]), [AUC_ROC] = [AUC ROC Maximo Ganador])` |
| `Threshold Optimo Youden J` / `Brier Score Ganador` / `Log Loss Ganador` | 01 Clasificacion y Scoring Crediticio | Punto de corte óptimo (Youden J) y calidad de calibración probabilística del modelo campeón | mismo patrón `CALCULATE(MAX(...), AUC_ROC = maximo)` |
| `TPR Regresion Logistica` / `TPR Random Forest` / `TPR Gradient Boosting` | 01 Clasificacion y Scoring Crediticio | Punto de la curva ROC de cada uno de los 3 modelos, para graficarlas superpuestas | `CALCULATE(MAX(ML_Curva_ROC[TPR]), ML_Curva_ROC[Modelo] = "...")` |
| `Clientes en Riesgo Critico` / `Moderado` / `Bajo` | 01 Clasificacion y Scoring Crediticio | Segmentación de la cartera de 350 clientes por nivel de score | `CALCULATE(COUNTROWS(ML_Scoring_Riesgo), [NivelRiesgo] = "...")` |
| `Semaforo Salud Cartera` / `Color Semaforo Cartera` | 01 Clasificacion y Scoring Crediticio | Semáforo de salud de cartera según % en riesgo crítico | `SWITCH(TRUE(), [Proporcion Cartera en Riesgo %] > 0.15, "ALTO RIESGO", ...)` |
| `Regla Decision Scoring Crediticio` | 01 Clasificacion y Scoring Crediticio | Texto de acción de mitigación (aval bancario, pago anticipado) | multi-línea |
| `Volumen Real Mensual` / `Forecast GBDT Mensual` / `Forecast SARIMAX Mensual` / `Forecast RandomForest Mensual` | 02 Forecasting de Demanda ML | Comparativo mensual real vs. los 3 forecasts | `SUM(ML_Forecasting_Comparativo[...])` |
| `RMSE GBDT` / `RMSE SARIMAX` / `MAE GBDT` / `MAPE GBDT %` / `MAPE SARIMAX %` | 02 Forecasting de Demanda ML | Error de forecast por modelo | `CALCULATE(MAX(ML_Metricas_Forecasting[RMSE]), [Modelo] = "Gradient_Boosting_Regressor")` |
| `Reduccion Error Forecast %` | 02 Forecasting de Demanda ML | % de mejora de RMSE del GBDT frente al benchmark SARIMAX | `CALCULATE(MAX(ML_Metricas_Forecasting[Reduccion_RMSE_vs_SARIMAX_Pct]), [Modelo] = "Gradient_Boosting_Regressor")` |
| `IC 95% Inferior/Superior Mensual` / `Intervalo Confianza 95 Amplitud` | 02 Forecasting de Demanda ML | Banda de confianza del forecast | `SUM(ML_Forecasting_Comparativo[IC_Inferior_95/IC_Superior_95])` |
| `CF-VaR 95% 30d` / `CF-VaR 99% 30d` | 03 Riesgo y Stress Testing VaR | Value at Risk del flujo de caja a 30 días (Monte Carlo, 10.000 senderos) | `CALCULATE(MAX(Riesgo_Stress_Testing_VaR[CF_VaR_95]), [HorizonteDias] = 30)` |
| `CVaR 95% Expected Shortfall` / `CVaR 99% Expected Shortfall` / `Buffer Liquidez Requerido 30d` | 03 Riesgo y Stress Testing VaR | Pérdida esperada más allá del VaR y colchón de liquidez recomendado | mismo patrón `CALCULATE(MAX(...), HorizonteDias = 30)` |
| `Buffer Solvencia Minimo Stress` / `Dias Cobertura Stress Minimo` | 03 Riesgo y Stress Testing VaR | Solvencia y días de cobertura remanentes en el peor escenario de reverse stress testing | `MIN(Riesgo_Reverse_Stress_Testing[BufferSolvenciaRestante])` / `MIN([DiasCoberturaRestante])` |
| `Escenario Mayor Riesgo` / `Semaforo Solvencia Stress` / `Color Semaforo Stress` | 03 Riesgo y Stress Testing VaR | Identifica y semaforiza el escenario de "Reverse Stress Breakpoint" | `CALCULATE(FIRSTNONBLANK(...[NombreEscenario], 1), [BufferSolvenciaRestante] = [Buffer Solvencia Minimo Stress])` |
| `Playbook Mitigacion Reverse Stress` | 03 Riesgo y Stress Testing VaR | Texto de contingencia (línea de crédito, cobertura) | multi-línea |
| `ATE Causal Descuentos DML` / `Benchmark OLS Descuentos` / `Sesgo Confusion Eliminado %` | 04 Inferencia Causal Econometrica | Efecto causal aislado (DML) vs. estimación ingenua OLS, y % de sesgo de selección eliminado | `CALCULATE(MAX(Inferencia_Causal_Resultados[CoeficienteEstimado]), [EfectoAnalizado] = "Efecto Causal ATE Descuentos Comerciales (DML)")` |
| `IC 95 Inferior ATE DML` / `IC 95 Superior ATE DML` | 04 Inferencia Causal Econometrica | Intervalo de confianza del ATE causal | mismo patrón, sobre `[IC_95_Inferior]`/`[IC_95_Superior]` |
| `Pass-Through Insumos ERPT` / `Pass-Through Domestico ERPT` | 04 Inferencia Causal Econometrica | Elasticidad de transmisión cambiaria a insumos secos y a precios domésticos | mismo patrón, filtrado por `EfectoAnalizado = "Pass-Through Cambiario en..."` |
| `ATE Causal Promedio Segmentos` / `ATE Causal Segmento Entrada` / `ATE Causal Segmento Icono` | 04 Inferencia Causal Econometrica | ATE causal por segmento de producto (Entrada/Varietales es el más elástico, Icono/Gran Reserva el menos) | `AVERAGE(Inferencia_Causal_Detalle_Segmento[ATE_Causal])`; `CALCULATE(MAX(...), [Segmento] = "...")` |
| `Prescripcion Pricing Causal` | 04 Inferencia Causal Econometrica | Texto de recomendación de pricing por elasticidad | multi-línea |

---

## 5. Convenciones y Disciplina Técnica

- **Nunca escribir JSON/TMDL a mano sin verificar patrones existentes primero.** Todo archivo `.tmdl` o PBIR (`visual.json`, `report.json`) debe editarse leyendo primero un ejemplo real y funcionando del mismo repo (mismo tipo de tabla, misma clase de medida) para replicar `lineageTag` únicos, indentación con tabs y estructura `partition ... = m|calculated`. Power BI Desktop es intolerante a desviaciones silenciosas de este formato: el archivo puede parsear como JSON/TMDL válido y aun así corromper el modelo al abrir.
- **Bug class detectado y corregido esta sesión — TMDL malformado en medidas multi-línea:** medidas DAX con bloques `VAR ... RETURN` de varias líneas requieren indentación consistente por tab respecto a la línea `measure 'Nombre' =`, y cada medida/columna nueva necesita un `lineageTag` (GUID) único — no reutilizado de otra medida por copy-paste. Un `lineageTag` duplicado o una indentación rota en el bloque `VAR/RETURN` no siempre falla al cargar, pero corrompe el árbol de dependencias del motor VertiPaq o produce resultados silenciosamente incorrectos. Lección de gobernanza: **validar el TMDL contra un ejemplo funcionando del mismo modelo antes de guardar**, no solo contra la sintaxis DAX en abstracto.
- **`CategoriaABC` (`Productos.tmdl`, proyecto 02) — caso de estudio de "JSON/TMDL válido no implica valor de negocio correcto":** existían simultáneamente dos clasificaciones ABC en el mismo modelo: (1) una columna estática `CategoriaABC` que mapeaba `Linea` de producto → Clase A/B/C con un diccionario fijo, ignorando el ingreso real por SKU, y (2) la medida `'Clasificacion ABC'` en `_Medidas_Comercial.tmdl`, que calcula la clase real vía `RANKX` + % acumulado de ingresos sobre `Ventas`. Ambas convivían mostrando clasificaciones contradictorias en la misma página (`p3_pareto`): el archivo TMDL era 100% válido sintácticamente, pero la columna estática era un valor de negocio fabricado. Se resolvió convirtiendo `CategoriaABC` en una columna calculada DAX con la **misma metodología y los mismos umbrales (75%/92%)** que la medida `'Clasificacion ABC'` ya existente (ver `Productos.tmdl` líneas 80-98), eliminando la contradicción sin duplicar lógica de negocio.
- **Causa raíz relacionada, en la capa de generación de datos:** antes de esta sesión, `generar_datos_historicos_ventas.py` generaba volumen de ventas por SKU de forma uniforme (9-20 transacciones/mes) sin importar el segmento, lo que producía una curva de Pareto irrealmente plana (67% de los SKUs caía en "Clase A"). Se corrigió introduciendo `SEGMENTO_VOL_BASE_MES` — rangos de volumen base diferenciados por segmento (p. ej. `Entrada: (35,70)` vs. `Gran Reserva / Icono: (3,9)`) — reflejando que los vinos de entrada/granel venden mucho más volumen que los íconos premium. Esta es la causa raíz real de por qué la clasificación ABC fabricada parecía "razonable" a simple vista pese a estar mal fundamentada: el dato de origen tampoco reflejaba la asimetría real de ventas por segmento.
- **Fuente única de verdad:** los 4 modelos semánticos importan desde el mismo parámetro M `RutaDatos` (definido en `expressions.tmdl` de cada proyecto, apuntando a `01_Limpieza_de_Datos/curated_gold`), evitando que cada modelo tenga su propia copia divergente de las tablas maestras.
- **`ML_Matriz_Confusion.csv` — decisión de diseño, no bug:** `ml_riesgo_prediccion.py` entrena y evalúa los 3 modelos de clasificación (Regresión Logística L2, Random Forest, Gradient Boosting), pero exporta la matriz de confusión **únicamente del modelo campeón** (el de mayor `AUC_ROC`), no de los 3. Es intencional: la matriz de confusión visualizada en `06` (página `p1_clasif`) debe corresponder al modelo que realmente se usaría en producción, no a un promedio o a los 3 candidatos mezclados. Esta invariante está protegida por el test `01_Limpieza_de_Datos/tests/test_business_value_sanity.py::test_ml_matriz_confusion_es_del_modelo_ganador`, que falla si `ML_Matriz_Confusion.csv` contiene un modelo distinto al de mayor AUC-ROC en `ML_Metricas_Clasificacion.csv`.

---

## 6. Cómo Regenerar el Pipeline Completo End-to-End

Ejecutar en este orden desde la raíz del repo (`Portfolio_Empresarial_PowerBI/`):

```bash
# 1) Generación de datos RAW (sintéticos, calibrados contra series reales BCRA/INDEC/INV)
python 01_Limpieza_de_Datos/generar_datos_historicos_ventas.py
python 01_Limpieza_de_Datos/generar_presupuesto_2025.py
# (los demás raw_*.csv — OPEX, centros de costo, planta, capital de trabajo,
#  plan de cuentas — son archivos estáticos versionados en raw/, no requieren generador)

# 2) ETL determinista: raw/ -> curated_gold/ (limpieza, unpivot, integridad referencial)
python 01_Limpieza_de_Datos/etl_pipeline_cleaner.py

# 3) Actualización de capa de datos derivada (geolocalización planta, inventario de
#    guarda, cuentas industriales, redistribución de OPEX fabril)
python 01_Limpieza_de_Datos/update_data_layer.py

# 4) Capa econométrica: corre los modelos y persiste outputs/*.json
python 05_Analisis_Econometrico/src/analisis_elasticidad_cointegracion.py
python 05_Analisis_Econometrico/src/estacionalidad_y_forecast.py

# 5) Export de resultados econométricos a curated_gold (elasticidad, estacionalidad,
#    forecast, cointegración, curva Rofex CIP real)
python 05_Analisis_Econometrico/src/exportar_resultados_powerbi.py

# 5b) ML de riesgo/forecasting, inferencia causal y stress testing financiero (orden
#     real verificado en .github/workflows/business-value-tests.yml)
python 05_Analisis_Econometrico/src/ml_riesgo_prediccion.py
python 05_Analisis_Econometrico/src/inferencia_causal_erpt.py
python 05_Analisis_Econometrico/src/modelo_miller_orr_var.py

# 6) Apertura en Power BI Desktop: abrir cada .pbip
#    (02_Control_de_Gestion/02_Control_de_Gestion.pbip,
#    03_Inteligencia_Comercial/03_Inteligencia_Comercial.pbip,
#    04_Operaciones_y_Planta/04_Operaciones_y_Planta.pbip,
#    06_Modelos_de_Riesgo_y_Prediccion/06_Riesgo.pbip) y refrescar (Home > Refresh).
#    Los 4 leen curated_gold/ vía el parámetro M RutaDatos, por lo que basta un solo
#    refresh por modelo tras regenerar la capa gold.
```

**Nota:** los pasos 1-5b son deterministas dado `np.random.seed`/`default_rng(42)`/`random_state=42` fijo en cada generador — re-ejecutarlos produce exactamente los mismos datos, salvo que cambien los CSV/JSON de `05_Analisis_Econometrico/data/real/` (series reales, actualizables desde las APIs de BCRA/INDEC). Esta secuencia exacta es la que corre `.github/workflows/business-value-tests.yml` en CI.
