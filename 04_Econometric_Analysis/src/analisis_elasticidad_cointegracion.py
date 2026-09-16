# -*- coding: utf-8 -*-
"""
Script reusable: elasticidad-precio de demanda domestica por segmento, y
tests de cointegracion (pass-through cambiario / pass-through inflacionario).

Importa la logica economica de `elasticidad.py` y `cointegracion.py` -- este
modulo solo prepara los datos (carga, agregacion a panel mensual, filtros de
canal) y orquesta las llamadas, no reimplementa la regresion ni el test ADF/
Engle-Granger.

Pensado para ser importado desde un notebook:
    from analisis_elasticidad_cointegracion import correr_todo
    correr_todo()
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from elasticidad import estimar_elasticidad, elasticidad_por_segmento
from cointegracion import test_engle_granger

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent  # 04_Econometric_Analysis
PROJECT_ROOT = BASE_DIR.parent  # Portfolio_Empresarial_PowerBI

FACT_VENTAS_PATH = PROJECT_ROOT / "00_Data_Engineering_ETL" / "curated_gold" / "fact_ventas_reales.csv"
DIM_PRODUCTOS_PATH = PROJECT_ROOT / "00_Data_Engineering_ETL" / "curated_gold" / "dim_productos.csv"
FX_PATH = BASE_DIR / "data" / "real" / "fx_mensual_2021_2025.csv"
IPC_PATH = BASE_DIR / "data" / "real" / "ipc_mensual_2021_2025.csv"

OUTPUT_DIR = BASE_DIR / "outputs"
ELASTICIDAD_OUTPUT_PATH = OUTPUT_DIR / "elasticidad_resultados.json"
COINTEGRACION_OUTPUT_PATH = OUTPUT_DIR / "cointegracion_resultados.json"

CANAL_EXPORTACION = "Exportacion Directa"

# Segmentos donde se espera mayor elasticidad (bienes de necesidad / commodity)
SEGMENTOS_ELASTICOS_ESPERADOS = {"Entrada", "Granel / Masivo"}
# Segmentos donde se espera menor elasticidad (bien de lujo / status)
SEGMENTOS_INELASTICOS_ESPERADOS = {"Gran Reserva / Icono"}


# ---------------------------------------------------------------------------
# Tarea 1: elasticidad-precio
# ---------------------------------------------------------------------------
def cargar_datos_ventas() -> tuple[pd.DataFrame, pd.DataFrame]:
    fact = pd.read_csv(FACT_VENTAS_PATH, parse_dates=["Fecha"])
    dim = pd.read_csv(DIM_PRODUCTOS_PATH)
    return fact, dim


def construir_panel_elasticidad(fact: pd.DataFrame, dim: pd.DataFrame) -> pd.DataFrame:
    """Panel mensual por SKU, SOLO canales domesticos (excluye Exportacion
    Directa: la demanda de exportacion responde a otra dinamica, tipo de
    cambio, no a precio domestico). Devuelve columnas log_volumen, log_precio,
    Mes (1-12, para efectos fijos estacionales) y Segmento."""
    domestico = fact[fact["CanalVenta"] != CANAL_EXPORTACION].copy()
    domestico["AnioMes"] = domestico["Fecha"].dt.to_period("M").astype(str)
    domestico["Mes"] = domestico["Fecha"].dt.month

    agg = (
        domestico.groupby(["ProductoID", "AnioMes", "Mes"], as_index=False)
        .agg(Volumen=("VolumenReal", "sum"), Ingresos=("IngresosReales", "sum"))
    )
    agg["Precio"] = agg["Ingresos"] / agg["Volumen"]  # precio promedio ponderado
    agg = agg[(agg["Volumen"] > 0) & (agg["Precio"] > 0)].copy()

    agg = agg.merge(dim[["ProductoID", "SKU", "Segmento"]], on="ProductoID", how="left")

    agg["log_volumen"] = np.log(agg["Volumen"])
    agg["log_precio"] = np.log(agg["Precio"])
    return agg


def _extraer_stats(modelo, coef: str = "log_precio") -> dict:
    return {
        "beta": float(modelo.params[coef]),
        "std_err": float(modelo.bse[coef]),
        "p_value": float(modelo.pvalues[coef]),
        "r2": float(modelo.rsquared),
        "n_obs": int(modelo.nobs),
    }


def correr_elasticidad(panel: pd.DataFrame) -> dict:
    """Corre el modelo global y por segmento. Devuelve dict {segmento: stats},
    con clave adicional 'GLOBAL' para el modelo agregado."""
    resultados = {}

    modelo_global = estimar_elasticidad(
        panel, log_vol_col="log_volumen", log_precio_col="log_precio",
        sku_col="SKU", mes_col="Mes",
    )
    resultados["GLOBAL"] = _extraer_stats(modelo_global)

    modelos_segmento = elasticidad_por_segmento(
        panel, segmento_col="Segmento",
        log_vol_col="log_volumen", log_precio_col="log_precio",
        sku_col="SKU", mes_col="Mes",
    )
    for seg, modelo in modelos_segmento.items():
        resultados[seg] = _extraer_stats(modelo)

    return resultados


def chequeo_sentido_economico(resultados: dict) -> str:
    """Compara beta de segmentos elasticos esperados (Entrada, Granel/Masivo)
    vs. inelasticos esperados (Gran Reserva/Icono). No fuerza nada, solo
    describe si el orden economico esperado se cumple."""
    elasticos = {k: v["beta"] for k, v in resultados.items() if k in SEGMENTOS_ELASTICOS_ESPERADOS}
    inelasticos = {k: v["beta"] for k, v in resultados.items() if k in SEGMENTOS_INELASTICOS_ESPERADOS}

    if not elasticos or not inelasticos:
        return "No se pudo evaluar el orden economico esperado: faltan segmentos comparables en los resultados."

    beta_mas_elastico_esperado = min(elasticos.values())  # mas negativo = mas elastico
    beta_menos_elastico_esperado = max(inelasticos.values())

    if beta_mas_elastico_esperado < beta_menos_elastico_esperado:
        return (
            f"OK -- orden economico esperado se cumple: segmentos de necesidad/commodity "
            f"({elasticos}) son mas elasticos (beta mas negativo) que Gran Reserva/Icono "
            f"({inelasticos})."
        )
    return (
        f"OBSERVACION -- el orden economico esperado NO se cumple en los datos: "
        f"segmentos de necesidad/commodity ({elasticos}) no resultaron mas elasticos que "
        f"Gran Reserva/Icono ({inelasticos}). Se reporta el resultado real, sin forzarlo."
    )


def guardar_resultados_elasticidad(resultados: dict, observacion: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"resultados_por_segmento": resultados, "chequeo_sentido_economico": observacion}
    with open(ELASTICIDAD_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def correr_tarea_elasticidad() -> dict:
    fact, dim = cargar_datos_ventas()
    panel = construir_panel_elasticidad(fact, dim)
    resultados = correr_elasticidad(panel)
    observacion = chequeo_sentido_economico(resultados)
    guardar_resultados_elasticidad(resultados, observacion)
    return {"resultados": resultados, "observacion": observacion}


# ---------------------------------------------------------------------------
# Tarea 2: cointegracion
# ---------------------------------------------------------------------------
def cargar_series_macro() -> tuple[pd.Series, pd.Series]:
    fx = pd.read_csv(FX_PATH, parse_dates=["date"]).set_index("date")["value"].rename("FX")
    ipc = pd.read_csv(IPC_PATH, parse_dates=["date"]).set_index("date")["value"].rename("IPC")
    return fx, ipc


def construir_serie_precio_exportacion(fact: pd.DataFrame) -> pd.Series:
    """Precio de exportacion nominal ARS mensual, promedio simple de
    PrecioRealUnit a nivel mercado (no por SKU), canal Exportacion Directa."""
    export = fact[fact["CanalVenta"] == CANAL_EXPORTACION].copy()
    export["AnioMes"] = export["Fecha"].dt.to_period("M").dt.to_timestamp()
    serie = export.groupby("AnioMes")["PrecioRealUnit"].mean().rename("PrecioExportacion")
    return serie


def construir_serie_precio_domestico(fact: pd.DataFrame) -> pd.Series:
    """Precio domestico nominal mensual, promedio ponderado (por volumen) de
    PrecioRealUnit a nivel mercado, canales domesticos."""
    domestico = fact[fact["CanalVenta"] != CANAL_EXPORTACION].copy()
    domestico["AnioMes"] = domestico["Fecha"].dt.to_period("M").dt.to_timestamp()
    domestico["ValorVentas"] = domestico["PrecioRealUnit"] * domestico["VolumenReal"]
    agg = domestico.groupby("AnioMes").agg(ValorVentas=("ValorVentas", "sum"), Volumen=("VolumenReal", "sum"))
    serie = (agg["ValorVentas"] / agg["Volumen"]).rename("PrecioDomestico")
    return serie


def correr_tests_cointegracion(fact: pd.DataFrame) -> dict:
    fx, ipc = cargar_series_macro()

    precio_exportacion = construir_serie_precio_exportacion(fact)
    precio_domestico = construir_serie_precio_domestico(fact)

    # Alinear por fecha (indices mensuales, mismo dia de mes esperado: MS)
    fx.index = fx.index.to_period("M").to_timestamp()
    ipc.index = ipc.index.to_period("M").to_timestamp()

    test_a = test_engle_granger(precio_exportacion, fx)  # pass-through cambiario
    test_b = test_engle_granger(precio_domestico, ipc)   # pass-through inflacionario

    return {
        "test_A_pass_through_cambiario": _limpiar_resultado_coint(test_a),
        "test_B_pass_through_inflacionario": _limpiar_resultado_coint(test_b),
    }


def _limpiar_resultado_coint(r: dict) -> dict:
    return {
        "orden_y": r["orden_y"],
        "orden_x": r["orden_x"],
        "es_valido": bool(r["es_valido"]),
        "estadistico": float(r["estadistico"]),
        "p_value": float(r["p_value"]),
        "conclusion": r["conclusion"],
    }


def guardar_resultados_cointegracion(resultados: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(COINTEGRACION_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)


def correr_tarea_cointegracion() -> dict:
    fact, _ = cargar_datos_ventas()
    resultados = correr_tests_cointegracion(fact)
    guardar_resultados_cointegracion(resultados)
    return resultados


# ---------------------------------------------------------------------------
# Orquestacion
# ---------------------------------------------------------------------------
def correr_todo() -> dict:
    elasticidad = correr_tarea_elasticidad()
    cointegracion = correr_tarea_cointegracion()
    return {"elasticidad": elasticidad, "cointegracion": cointegracion}


if __name__ == "__main__":
    salida = correr_todo()

    print("=== ELASTICIDAD POR SEGMENTO ===")
    for seg, stats in salida["elasticidad"]["resultados"].items():
        print(f"  {seg:>20s}: beta={stats['beta']:.4f}  se={stats['std_err']:.4f}  "
              f"p={stats['p_value']:.4f}  R2={stats['r2']:.3f}  n={stats['n_obs']}")
    print(f"  Chequeo: {salida['elasticidad']['observacion']}")

    print("\n=== COINTEGRACION ===")
    for nombre, r in salida["cointegracion"].items():
        print(f"  {nombre}: {r['conclusion']}")

    print(f"\nGuardado en: {ELASTICIDAD_OUTPUT_PATH}")
    print(f"Guardado en: {COINTEGRACION_OUTPUT_PATH}")
