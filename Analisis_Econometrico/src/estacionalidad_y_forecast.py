# -*- coding: utf-8 -*-
"""
Estacionalidad (STL) y forecasting (SARIMA) sobre la demanda domestica agregada
de vino (fact_ventas_reales.csv, canales domesticos, 2021-2025).

Funciones separadas y reusables -- el notebook final importa este modulo, no
reimplementa nada aca. La descomposicion STL se delega 100% a
`seasonality.descomponer_estacional` (ya existente, con self-test propio).

Validacion vs sinteticos: `indice_estacional_inv_2024.csv` (consumo domestico
real de vino en Argentina, INV 2024) fue la referencia usada para CALIBRAR la
estacionalidad de las ventas sinteticas en fact_ventas_reales.csv. Por lo tanto
recuperar ese mismo patron via STL es una validacion de que la metodologia
(STL) funciona -- NO es evidencia de negocio independiente. Ver docstring de
`comparar_con_indice_real`.
"""
from __future__ import annotations

import json
import itertools
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from seasonality import descomponer_estacional

# ---------------------------------------------------------------------------
# Paths (todos relativos a la raiz del proyecto Portfolio_Empresarial_PowerBI)
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]
FACT_VENTAS_PATH = ROOT / "Ingenieria_de_Datos" / "curated_gold" / "fact_ventas_reales.csv"
INDICE_REAL_PATH = ROOT / "Analisis_Econometrico" / "data" / "real" / "indice_estacional_inv_2024.csv"
OUTPUTS_DIR = ROOT / "Analisis_Econometrico" / "outputs"

CANAL_EXCLUIDO = "Exportacion Directa"


# ---------------------------------------------------------------------------
# TAREA 1 -- agregacion y descomposicion STL
# ---------------------------------------------------------------------------
def construir_serie_mensual_domestica(
    fact_ventas_path: Path = FACT_VENTAS_PATH,
    canal_excluido: str = CANAL_EXCLUIDO,
) -> pd.Series:
    """
    Agrega fact_ventas_reales.csv por mes calendario (sum(VolumenReal)),
    excluyendo el canal de exportacion (demanda domestica agregada).

    Devuelve pd.Series indexada por DatetimeIndex mensual (freq='MS'),
    2021-01 a 2025-12 (60 observaciones), sin NaN (meses faltantes se
    completan con asfreq y se validan).
    """
    df = pd.read_csv(fact_ventas_path, usecols=["Fecha", "VolumenReal", "CanalVenta"])
    df = df[df["CanalVenta"] != canal_excluido].copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    df["mes"] = df["Fecha"].values.astype("datetime64[M]")

    serie = df.groupby("mes")["VolumenReal"].sum().sort_index()
    serie.index = pd.DatetimeIndex(serie.index, freq=None)
    serie = serie.asfreq("MS")

    if serie.isna().any():
        meses_faltantes = serie[serie.isna()].index.tolist()
        raise ValueError(f"Serie mensual con huecos, no se puede interpolar silenciosamente: {meses_faltantes}")

    serie.name = "VolumenReal_mensual_domestico"
    return serie


def comparar_con_indice_real(
    indice_recuperado: pd.Series,
    indice_real_path: Path = INDICE_REAL_PATH,
) -> dict:
    """
    Compara el indice estacional recuperado por STL contra el indice real de
    consumo domestico de vino (INV 2024) usado para calibrar los datos.

    IMPORTANTE (honestidad metodologica): este indice real NO es un target
    independiente -- fue la referencia con la que se calibro la estacionalidad
    sintetica de fact_ventas_reales.csv. Una correlacion alta aca confirma que
    STL recupera correctamente el patron que se inyecto (validacion de
    tecnica), no que el patron estacional sea un hallazgo de negocio nuevo.

    Devuelve dict con correlacion de Pearson y tabla mes a mes.
    """
    real = pd.read_csv(indice_real_path).set_index("mes")["indice_estacional_2024_real"]
    real.index.name = "mes"

    recuperado = indice_recuperado.copy()
    recuperado.index.name = "mes"

    tabla = pd.DataFrame({
        "indice_estacional_recuperado_stl": recuperado,
        "indice_estacional_real_inv2024": real,
    })
    tabla["diferencia_absoluta"] = (tabla["indice_estacional_recuperado_stl"] - tabla["indice_estacional_real_inv2024"]).abs()

    correlacion = float(tabla["indice_estacional_recuperado_stl"].corr(tabla["indice_estacional_real_inv2024"]))

    return {
        "correlacion_con_indice_real": correlacion,
        "tabla_mes_a_mes": tabla.reset_index().to_dict(orient="records"),
        "nota_metodologica": (
            "El indice real INV2024 fue la referencia usada para calibrar la estacionalidad "
            "sintetica de fact_ventas_reales.csv. Esta comparacion valida que STL recupera el "
            "patron inyectado (validacion de metodo), no es evidencia de negocio independiente."
        ),
    }


def ejecutar_tarea1_estacionalidad(
    fact_ventas_path: Path = FACT_VENTAS_PATH,
    indice_real_path: Path = INDICE_REAL_PATH,
    outputs_dir: Path = OUTPUTS_DIR,
) -> dict:
    """Corre la Tarea 1 completa y persiste estacionalidad_resultados.json."""
    serie = construir_serie_mensual_domestica(fact_ventas_path)
    trend, seasonal, resid, indice = descomponer_estacional(serie, periodo=12, robust=True)

    comparacion = comparar_con_indice_real(indice, indice_real_path)

    resultado = {
        "n_observaciones": int(len(serie)),
        "rango_fechas": [str(serie.index.min().date()), str(serie.index.max().date())],
        "indice_estacional_recuperado": {int(m): round(float(v), 4) for m, v in indice.items()},
        "correlacion_con_indice_real": round(comparacion["correlacion_con_indice_real"], 4),
        "tabla_mes_a_mes": comparacion["tabla_mes_a_mes"],
        "nota_metodologica": comparacion["nota_metodologica"],
        "trend": {str(k.date()): round(float(v), 2) for k, v in trend.items()},
        "resid_std": round(float(resid.std()), 4),
    }

    outputs_dir.mkdir(parents=True, exist_ok=True)
    out_path = outputs_dir / "estacionalidad_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado


# ---------------------------------------------------------------------------
# TAREA 2 -- SARIMA con backtest 12 meses
# ---------------------------------------------------------------------------
def seleccionar_mejor_sarima(
    train: pd.Series,
    ordenes_no_estacionales: Optional[list] = None,
    ordenes_estacionales: Optional[list] = None,
    period: int = 12,
):
    """
    Grid chico sobre (p,d,q) x (P,D,Q,period); se queda con el de menor AIC en
    train. Devuelve (mejor_resultado_fit, mejor_orden_tuple, mejor_orden_estacional_tuple).
    """
    if ordenes_no_estacionales is None:
        ordenes_no_estacionales = [(1, 1, 1), (0, 1, 1)]
    if ordenes_estacionales is None:
        ordenes_estacionales = [(1, 1, 1, period), (0, 1, 1, period)]

    candidatos = []
    # Se emparejan indice a indice (no producto cartesiano completo) para
    # mantener el grid chico segun lo pedido: (1,1,1)x(1,1,1,12) y
    # (0,1,1)x(0,1,1,12). Si se pasan listas de distinto largo, se usa
    # producto cartesiano.
    if len(ordenes_no_estacionales) == len(ordenes_estacionales):
        pares = list(zip(ordenes_no_estacionales, ordenes_estacionales))
    else:
        pares = list(itertools.product(ordenes_no_estacionales, ordenes_estacionales))

    mejor_aic = np.inf
    mejor_fit = None
    mejor_orden = None
    mejor_orden_estacional = None

    for orden, orden_estacional in pares:
        try:
            modelo = SARIMAX(
                train,
                order=orden,
                seasonal_order=orden_estacional,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            fit = modelo.fit(disp=False)
            candidatos.append({"orden": orden, "orden_estacional": orden_estacional, "aic": float(fit.aic)})
            if fit.aic < mejor_aic:
                mejor_aic = fit.aic
                mejor_fit = fit
                mejor_orden = orden
                mejor_orden_estacional = orden_estacional
        except Exception as e:
            candidatos.append({"orden": orden, "orden_estacional": orden_estacional, "aic": None, "error": str(e)})

    if mejor_fit is None:
        raise RuntimeError(f"Ningun modelo SARIMA convergio. Candidatos: {candidatos}")

    return mejor_fit, mejor_orden, mejor_orden_estacional, candidatos


def calcular_mape_rmse(real: np.ndarray, pred: np.ndarray) -> dict:
    real = np.asarray(real, dtype=float)
    pred = np.asarray(pred, dtype=float)
    mape = float(np.mean(np.abs((real - pred) / real)) * 100)
    rmse = float(np.sqrt(np.mean((real - pred) ** 2)))
    return {"MAPE": round(mape, 2), "RMSE": round(rmse, 2)}


def ejecutar_tarea2_forecast(
    fact_ventas_path: Path = FACT_VENTAS_PATH,
    outputs_dir: Path = OUTPUTS_DIR,
    n_test: int = 12,
) -> dict:
    """Corre la Tarea 2 completa (backtest SARIMA 12m) y persiste forecast_resultados.json."""
    serie = construir_serie_mensual_domestica(fact_ventas_path)

    train = serie.iloc[:-n_test]
    test = serie.iloc[-n_test:]

    mejor_fit, orden, orden_estacional, candidatos = seleccionar_mejor_sarima(train)

    forecast_res = mejor_fit.get_forecast(steps=n_test)
    forecast_media = forecast_res.predicted_mean
    conf_int = forecast_res.conf_int(alpha=0.05)

    metricas = calcular_mape_rmse(test.values, forecast_media.values)

    resultado = {
        "orden_modelo": {"order": list(orden), "seasonal_order": list(orden_estacional)},
        "aic_train": round(float(mejor_fit.aic), 2),
        "candidatos_grid": candidatos,
        "n_train": int(len(train)),
        "n_test": int(len(test)),
        "MAPE": metricas["MAPE"],
        "RMSE": metricas["RMSE"],
        "forecast_12m": {str(k.date()): round(float(v), 2) for k, v in forecast_media.items()},
        "real_12m": {str(k.date()): round(float(v), 2) for k, v in test.items()},
        "intervalo_confianza_95": {
            str(k.date()): [round(float(row.iloc[0]), 2), round(float(row.iloc[1]), 2)]
            for k, row in conf_int.iterrows()
        },
    }

    outputs_dir.mkdir(parents=True, exist_ok=True)
    out_path = outputs_dir / "forecast_resultados.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado


if __name__ == "__main__":
    print("=== TAREA 1: Estacionalidad STL ===")
    r1 = ejecutar_tarea1_estacionalidad()
    print(f"n_observaciones={r1['n_observaciones']}  rango={r1['rango_fechas']}")
    print(f"Correlacion STL vs indice real INV2024: {r1['correlacion_con_indice_real']}")

    print("\n=== TAREA 2: Forecast SARIMA (backtest 12m) ===")
    r2 = ejecutar_tarea2_forecast()
    print(f"Modelo elegido: order={r2['orden_modelo']['order']} seasonal_order={r2['orden_modelo']['seasonal_order']} (AIC train={r2['aic_train']})")
    print(f"MAPE={r2['MAPE']}%  RMSE={r2['RMSE']}")
