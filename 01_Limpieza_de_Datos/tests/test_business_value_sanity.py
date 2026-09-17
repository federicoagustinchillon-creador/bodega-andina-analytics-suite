# -*- coding: utf-8 -*-
"""
Tests de VALOR DE NEGOCIO sobre curated_gold y outputs econometricos.

A diferencia de `pbir validate` (que solo confirma que el JSON/TMDL es
estructuralmente valido), estos tests recalculan las metricas criticas
directamente desde los datos crudos y verifican que el VALOR tenga sentido
economico real -- el mismo tipo de chequeo que destapo el bug de
'Tasa Eficiencia Planta' invertida (100.9%) y el de CategoriaABC fabricado.

Correr con: pytest 01_Limpieza_de_Datos/tests/ -v
"""
import json
from pathlib import Path

import pandas as pd
import pytest

BASE = Path(__file__).resolve().parent.parent
GOLD = BASE / "curated_gold"
ECON_OUT = BASE.parent / "05_Analisis_Econometrico" / "outputs"


@pytest.fixture(scope="module")
def quality_report():
    return json.load(open(BASE / "data_quality_report.json", encoding="utf-8"))


@pytest.fixture(scope="module")
def ventas():
    return pd.read_csv(GOLD / "Ventas.csv")


@pytest.fixture(scope="module")
def productos():
    return pd.read_csv(GOLD / "Productos.csv")


@pytest.fixture(scope="module")
def capital_trabajo():
    return pd.read_csv(GOLD / "CapitalTrabajo.csv")


@pytest.fixture(scope="module")
def opex():
    return pd.read_csv(GOLD / "GastosOperativos.csv")


# --------------------------------------------------------------- integridad --
def test_sin_huerfanas_sin_resolver(quality_report):
    """Toda clave huerfana detectada por el ETL debe haber sido resuelta (cuarentena/fix), no colada."""
    for tabla, d in quality_report["tablas_procesadas"].items():
        detectadas = d.get("claves_huerfanas_detectadas", 0)
        resueltas = d.get("claves_huerfanas_resueltas", 0)
        assert resueltas == detectadas, f"{tabla}: {detectadas - resueltas} huerfanas sin resolver"


def test_tasa_validez_alta(quality_report):
    for tabla, d in quality_report["tablas_procesadas"].items():
        tasa = float(d["tasa_validez"].rstrip("%"))
        assert tasa >= 99.0, f"{tabla}: tasa de validez {tasa}% por debajo del minimo aceptable"


def test_ventas_referencian_productos_existentes(ventas, productos):
    huerfanos = set(ventas["ProductoID"]) - set(productos["ProductoID"])
    assert not huerfanos, f"ProductoID en ventas sin dimension: {huerfanos}"


# ------------------------------------------------------------ valor real --
def test_abc_pareto_concentracion_realista(ventas):
    """Regresion del bug: volumen uniforme por SKU generaba un Pareto irreal
    (67% de los SKUs en Clase A). Con distribucion de volumen por segmento,
    la Clase A (<=75% de ingresos acumulados) debe ser una FRACCION MINORITARIA
    del catalogo -- ni tan plana como antes, ni un monopolio irreal de 1-2 SKUs."""
    rev = ventas.groupby("ProductoID")["IngresosReales"].sum().sort_values(ascending=False)
    cum_pct = rev.cumsum() / rev.sum()
    clase_a = int((cum_pct <= 0.75).sum())
    n_total = len(rev)
    assert 6 <= clase_a <= 20, (
        f"Clase A = {clase_a}/{n_total} SKUs ({100*clase_a/n_total:.1f}%) -- "
        "fuera del rango realista para un catalogo curado de 36 SKUs (esperado ~15-55%)"
    )


def test_margen_bruto_plausible(ventas):
    ingresos = ventas["IngresosReales"].sum()
    margen = ventas["MargenBrutoReal"].sum()
    margen_pct = margen / ingresos
    assert 0.0 < margen_pct < 1.0, f"Margen bruto {margen_pct:.1%} fuera de rango [0%, 100%]"
    assert 0.25 <= margen_pct <= 0.75, (
        f"Margen bruto {margen_pct:.1%} atipico para vitivinicultura premium/export (esperado 25%-75%)"
    )


def test_tasa_eficiencia_planta_no_invertida(opex):
    """Regresion del bug original (100.9% con Plan/Real invertido). Real/Plan debe
    rondar 1.0 -- un desvio de 3 ordenes de magnitud (ej. 0.30) delata una formula invertida."""
    fabril = opex[opex["CentroCostoID"].isin(["CC-101", "CC-102", "CC-103"])]
    costo_real = fabril["OPEXReal"].sum()
    costo_presupuesto = fabril["OPEXPresupuestado"].sum()
    ratio = costo_real / costo_presupuesto
    assert 0.80 <= ratio <= 1.20, f"Costo Real/Presupuesto Fabril = {ratio:.3f} -- fuera de banda realista [0.80, 1.20]"


def test_ratio_cobertura_proveedores_direccion(capital_trabajo):
    """Regresion del bug encontrado en esta sesion (formula invertida: Pagar/Activo
    en vez de Activo/Pagar). El activo operativo liquido debe superar a cuentas por
    pagar (empresa con capacidad de cobertura), no al reves."""
    activo_liquido = capital_trabajo["CuentasPorCobrar"].sum() + capital_trabajo["Inventario"].sum()
    cuentas_pagar = capital_trabajo["CuentasPorPagar"].sum()
    ratio = activo_liquido / cuentas_pagar
    assert ratio > 1.0, f"Ratio Cobertura Proveedores = {ratio:.2f}x -- activo liquido no cubre pasivo (revisar direccion de la formula)"
    assert ratio < 10.0, f"Ratio Cobertura Proveedores = {ratio:.2f}x -- implausiblemente alto, revisar datos"


# ------------------------------------------------------ econometria real --
def test_elasticidad_orden_economico_esperado():
    """El motor de elasticidad ya calcula este chequeo (chequeo_sentido_economico);
    lo formalizamos como test para que una regresion en los datos de ventas lo rompa
    en CI en vez de pasar desapercibido."""
    d = json.load(open(ECON_OUT / "elasticidad_resultados.json", encoding="utf-8"))
    assert d["chequeo_sentido_economico"].startswith("OK"), d["chequeo_sentido_economico"]


def test_forecast_error_razonable():
    d = json.load(open(ECON_OUT / "forecast_resultados.json", encoding="utf-8"))
    assert d["MAPE"] < 15.0, f"MAPE del forecast SARIMA = {d['MAPE']}% -- demasiado alto para ser presentable"


def test_estacionalidad_correlaciona_con_indice_real():
    d = json.load(open(ECON_OUT / "estacionalidad_resultados.json", encoding="utf-8"))
    corr = d["correlacion_con_indice_real"]
    assert corr > 0.7, f"Correlacion STL vs. indice estacional real INV2024 = {corr:.3f} -- deberia ser alta si el patron es genuino"


# ------------------------------------ modelos de riesgo, ML y Miller-Orr --
def test_miller_orr_calibracion_coherente():
    """Valida la consistencia teorica del Modelo de Miller-Orr (L < z < h)."""
    df_mo = pd.read_csv(GOLD / "Tesoreria_Miller_Orr_Diario.csv")
    L = df_mo["BandaInferior_L"].iloc[0]
    z = df_mo["PuntoRetorno_Z"].iloc[0]
    h = df_mo["BandaSuperior_H"].iloc[0]
    assert L < z < h, f"Violacion de bandas Miller-Orr: L={L}, z={z}, h={h}"
    assert (df_mo["SaldoOcioso"] >= 0).all(), "Existen saldos ociosos negativos"
    assert (df_mo["CostoOportunidadDiario"] >= 0).all(), "Existen costos de oportunidad negativos"


def test_ml_clasificacion_auc_y_recall():
    """Valida que los modelos de clasificacion de riesgo superen los umbrales minimos de calidad."""
    df_met = pd.read_csv(GOLD / "ML_Metricas_Clasificacion.csv")
    mejor_auc = df_met["AUC_ROC"].max()
    assert mejor_auc >= 0.70, f"AUC-ROC del mejor modelo ({mejor_auc:.4f}) es inferior al umbral admisible (0.70)"
    mejor_rec = df_met["Recall"].max()
    assert mejor_rec >= 0.85, f"Recall en mora/quiebre ({mejor_rec:.4f}) es inferior al 85%"


def test_ml_forecasting_precision():
    """Valida que el forecasting supervisado tenga un error porcentual controlado y buen ajuste."""
    df_fc = pd.read_csv(GOLD / "ML_Metricas_Forecasting.csv")
    gb_row = df_fc[df_fc["Modelo"] == "Gradient_Boosting_Regressor"].iloc[0]
    assert gb_row["MAPE_Pct"] < 10.0, f"MAPE GBDT = {gb_row['MAPE_Pct']}% es demasiado alto"
    assert gb_row["R2_Score"] > 0.80, f"R2 GBDT = {gb_row['R2_Score']} no explica suficiente varianza"


def test_stress_testing_var_orden_probabilistico():
    """Valida la coherencia de colas: VaR 99% >= VaR 95% y CVaR >= VaR."""
    df_var = pd.read_csv(GOLD / "Riesgo_Stress_Testing_VaR.csv")
    row_30d = df_var[df_var["HorizonteDias"] == 30].iloc[0]
    assert row_30d["CF_VaR_99"] >= row_30d["CF_VaR_95"], "Inconsistencia: VaR 99% menor que VaR 95%"
    assert row_30d["CVaR_95_ExpectedShortfall"] >= row_30d["CF_VaR_95"], "Inconsistencia: Expected Shortfall menor que VaR 95%"


def test_inferencia_causal_dml_significativa():
    """Valida que el Double Machine Learning identifique un efecto causal estadisticamente significativo."""
    df_cau = pd.read_csv(GOLD / "Inferencia_Causal_Resultados.csv")
    row_dml = df_cau[df_cau["EfectoAnalizado"].str.contains("ATE")].iloc[0]
    assert row_dml["P_Valor"] < 0.05, f"Efecto ATE no significativo: p={row_dml['P_Valor']}"
    assert row_dml["CoeficienteEstimado"] > 0, "Efecto ATE deberia ser positivo (a mayor descuento, mayor volumen demandado)"
    assert row_dml["SesgoEliminadoPct"] > 50.0, "DML deberia corregir mas del 50% del sesgo de seleccion"


def test_ml_forecasting_ganador_es_el_de_menor_rmse():
    """Regresion: ModeloGanador/Ranking_Precision estaban hardcodeados a 'Gradient Boosting' sin
    comparar RMSE real -- el benchmark SARIMAX en realidad supera al ensamble ML en este backtest.
    El ganador declarado debe ser siempre el de menor RMSE, sea cual sea."""
    df_met = pd.read_csv(GOLD / "ML_Metricas_Forecasting.csv")
    ganador_por_rmse = df_met.loc[df_met["RMSE"].idxmin(), "Modelo"]
    ganador_declarado = df_met.loc[df_met["Ranking_Precision"] == 1, "Modelo"].iloc[0]
    assert ganador_declarado == ganador_por_rmse, (
        f"Ranking_Precision=1 declara '{ganador_declarado}' pero el menor RMSE real es de '{ganador_por_rmse}'"
    )

    df_fc = pd.read_csv(GOLD / "ML_Forecasting_Comparativo.csv")
    nombre_legible = {
        "Gradient_Boosting_Regressor": "Gradient Boosting",
        "Random_Forest_Regressor": "Random Forest",
        "Benchmark_SARIMAX_1_1_1": "Benchmark SARIMAX",
    }[ganador_por_rmse]
    assert (df_fc["ModeloGanador"] == nombre_legible).all(), (
        f"ModeloGanador en ML_Forecasting_Comparativo no coincide con el modelo de menor RMSE ({nombre_legible})"
    )


def test_ml_auc_no_sospechosamente_perfecto():
    """Un AUC-ROC cercano a 1.0 sobre datos de negocio reales delata data leakage, no un buen modelo."""
    df_met = pd.read_csv(GOLD / "ML_Metricas_Clasificacion.csv")
    assert (df_met["AUC_ROC"] < 0.98).all(), (
        f"AUC-ROC sospechosamente perfecto ({df_met['AUC_ROC'].max():.4f}) -- revisar fuga de datos (variable "
        "objetivo filtrandose a los features)"
    )


def test_ml_matriz_confusion_es_del_modelo_ganador():
    """La matriz de confusion exportada (solo el modelo campeon, por diseno) debe corresponder
    al modelo con mayor AUC-ROC, no a cualquier otro candidato."""
    df_cm = pd.read_csv(GOLD / "ML_Matriz_Confusion.csv")
    df_met = pd.read_csv(GOLD / "ML_Metricas_Clasificacion.csv")
    ganador = df_met.sort_values("AUC_ROC", ascending=False).iloc[0]["Modelo"]
    modelos_matriz = set(df_cm["Modelo"])
    assert modelos_matriz == {ganador}, (
        f"Matriz de confusion pertenece a {modelos_matriz}, pero el modelo ganador por AUC-ROC es '{ganador}'"
    )
    total = df_cm["Conteo"].sum()
    assert total > 0, "Matriz de confusion vacia"


def test_columnas_pct_mantienen_escala_esperada():
    """Regresion: 'Reduccion_RMSE_vs_SARIMAX_Pct' y 'SesgoEliminadoPct' se generan en escala
    porcentual (73.71 = 73.71%), no como fraccion (0.7371) -- las medidas DAX que las leen
    (p.ej. 'Sesgo Eliminado % (Fila)') dividen por 100 asumiendo esa escala. Si algun cambio
    futuro en el generador Python las pasa a fraccion sin avisar, las tarjetas/tablas del
    dashboard mostrarian el valor 100x mas chico en silencio -- este test detecta ese cambio
    de escala, no reemplaza la revision visual en Power BI Desktop."""
    mf = pd.read_csv(GOLD / "ML_Metricas_Forecasting.csv")
    assert mf["Reduccion_RMSE_vs_SARIMAX_Pct"].abs().max() > 1.5, (
        "Reduccion_RMSE_vs_SARIMAX_Pct parece haber pasado a escala fraccion (0-1) -- "
        "la medida 'Reduccion RMSE % (Fila)' quedaria 100x mas chica"
    )
    ic = pd.read_csv(GOLD / "Inferencia_Causal_Resultados.csv")
    assert ic["SesgoEliminadoPct"].max() > 1.5, (
        "SesgoEliminadoPct parece haber pasado a escala fraccion (0-1) -- "
        "la medida 'Sesgo Eliminado % (Fila)' quedaria 100x mas chica"
    )


def test_cumplimiento_presupuesto_indexado_multianual(ventas, productos):
    """Valida la coherencia economica del presupuesto 2021-2025 indexado a inflacion INDEC y FX.
    Regresion del bug de 2800% / 1333%: el presupuesto debe cubrir los 5 anos (60 meses x 36 SKUs x 2 CC),
    con cumplimiento anual calibrado estrictamente en la banda institucional del 98.0% al 102.5%."""
    df_p = pd.read_csv(GOLD / "PresupuestoVentas.csv")
    assert len(df_p) == 4320, f"PresupuestoVentas tiene {len(df_p)} filas, esperado 4320 (60 meses x 36 SKUs x 2 CC)"
    
    # Integridad referencial con productos
    huerfanos = set(df_p["ProductoID"]) - set(productos["ProductoID"])
    assert not huerfanos, f"ProductoID en presupuesto sin dimension: {huerfanos}"
    
    # Cumplimiento por anio
    ventas["Year"] = ventas["DateKey"].astype(str).str[:4]
    df_p["Year"] = df_p["DateKey"].astype(str).str[:4]
    
    v_yr = ventas.groupby("Year")["IngresosReales"].sum()
    p_yr = df_p.groupby("Year")["IngresosPresupuestados"].sum()
    
    for anio in ["2021", "2022", "2023", "2024", "2025"]:
        assert anio in p_yr, f"Falta presupuesto para el anio {anio}"
        cumpl = (v_yr[anio] / p_yr[anio]) * 100.0
        assert 98.0 <= cumpl <= 102.5, (
            f"Cumplimiento Presupuesto en {anio} = {cumpl:.2f}% fuera de banda [98.0%, 102.5%]"
        )
        
    tot_v = ventas["IngresosReales"].sum()
    tot_p = df_p["IngresosPresupuestados"].sum()
    tot_cumpl = (tot_v / tot_p) * 100.0
    assert 99.5 <= tot_cumpl <= 101.5, f"Cumplimiento total 5 anos = {tot_cumpl:.2f}% fuera de banda [99.5%, 101.5%]"


