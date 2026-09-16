# -*- coding: utf-8 -*-
"""
Descomposicion estacional real (STL) -- requiere series >= 24 meses (2 ciclos
completos) para separar tendencia, estacionalidad y residuo con sentido
estadistico. Con 1 solo anio (12 puntos) no hay grados de libertad para
distinguir estacionalidad de ruido; por eso el dataset se expande a 2021-2025.
"""
import pandas as pd
from statsmodels.tsa.seasonal import STL


def descomponer_estacional(serie: pd.Series, periodo: int = 12, robust: bool = True):
    """
    serie: pd.Series indexada por fecha mensual (DatetimeIndex, freq='MS'), sin NaN.
    Devuelve (trend, seasonal, resid, indice_estacional_normalizado).
    El indice estacional normalizado promedia el componente 'seasonal' por
    mes-calendario y lo expresa como ratio sobre 1.0 (>1 = mes por encima del
    promedio anual, <1 = por debajo) -- es lo que se usa para calibrar
    generacion de datos sinteticos con estacionalidad empirica real.
    """
    if len(serie) < 2 * periodo:
        raise ValueError(
            f"STL requiere al menos {2*periodo} observaciones (2 ciclos); se recibieron {len(serie)}"
        )
    res = STL(serie, period=periodo, robust=robust).fit()
    # 'seasonal' es aditivo y centrado en ~0 por construccion de STL; para
    # expresarlo como indice multiplicativo (~1.0 = sin efecto estacional) se
    # normaliza el swing aditivo contra el nivel medio de la tendencia, no
    # contra la propia media de 'seasonal' (que es ~0 y produce division
    # inestable).
    nivel_medio = res.trend.mean()
    swing_por_mes = res.seasonal.groupby(res.seasonal.index.month).mean()
    indice = 1 + (swing_por_mes / nivel_medio)
    indice.name = "indice_estacional"
    return res.trend, res.seasonal, res.resid, indice


if __name__ == "__main__":
    import numpy as np
    rng = pd.date_range("2021-01-01", periods=48, freq="MS")
    trend = np.linspace(100, 140, 48)
    seasonal = 10 * np.sin(2 * np.pi * rng.month / 12)
    noise = np.random.default_rng(0).normal(0, 2, 48)
    s = pd.Series(trend + seasonal + noise, index=rng)
    t, se, r, idx = descomponer_estacional(s)
    print("Indice estacional recuperado (deberia oscilar ~1.0, pico en marzo-abril):")
    print(idx.round(3))
    assert abs(idx.mean() - 1.0) < 0.05
    assert idx.max() > 1.05 and idx.min() < 0.95, "deberia detectar variacion estacional real"
    print("OK: descomposicion STL funcional")
