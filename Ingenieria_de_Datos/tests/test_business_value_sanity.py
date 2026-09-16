# -*- coding: utf-8 -*-
"""
Tests de VALOR DE NEGOCIO sobre curated_gold y outputs econometricos.

A diferencia de `pbir validate` (que solo confirma que el JSON/TMDL es
estructuralmente valido), estos tests recalculan las metricas criticas
directamente desde los datos crudos y verifican que el VALOR tenga sentido
economico real -- el mismo tipo de chequeo que destapo el bug de
'Tasa Eficiencia Planta' invertida (100.9%) y el de CategoriaABC fabricado.

Correr con: pytest Ingenieria_de_Datos/tests/ -v
"""
import json
from pathlib import Path

import pandas as pd
import pytest

BASE = Path(__file__).resolve().parent.parent
GOLD = BASE / "curated_gold"
ECON_OUT = BASE.parent / "Analisis_Econometrico" / "outputs"


@pytest.fixture(scope="module")
def quality_report():
    return json.load(open(BASE / "data_quality_report.json", encoding="utf-8"))


@pytest.fixture(scope="module")
def ventas():
    return pd.read_csv(GOLD / "fact_ventas_reales.csv")


@pytest.fixture(scope="module")
def productos():
    return pd.read_csv(GOLD / "dim_productos.csv")


@pytest.fixture(scope="module")
def capital_trabajo():
    return pd.read_csv(GOLD / "fact_capital_trabajo.csv")


@pytest.fixture(scope="module")
def opex():
    return pd.read_csv(GOLD / "fact_opex_mensual.csv")


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
