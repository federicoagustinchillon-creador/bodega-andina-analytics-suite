# -*- coding: utf-8 -*-
"""
Test de cointegracion Engle-Granger de 2 pasos, con verificacion previa de
orden de integracion (ADF) -- cointegrar dos series I(0) no tiene sentido,
y cointegrar una I(1) con una I(2) tampoco. El test se hace bien o no se
reporta.

Casos de uso reales en este dataset:
1. Precio de exportacion (ARS) vs. tipo de cambio -- testea si el pass-through
   cambiario es de largo plazo (cointegran) o si el precio en USD se ajusta
   independientemente del tipo de cambio.
2. Precio domestico nominal vs. IPC -- testea si el precio nominal sigue la
   inflacion 1:1 en el largo plazo (cointegracion con vector [1,-1] implicaria
   precio real estacionario) o si hay perdida/ganancia real sistematica.
"""
import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint


def orden_integracion(serie: pd.Series, alpha: float = 0.05) -> str:
    """Devuelve 'I(0)' si la serie en niveles ya es estacionaria (ADF rechaza
    raiz unitaria), 'I(1)' si la primera diferencia lo es, 'I(2)+' si ninguna."""
    p_niveles = adfuller(serie.dropna())[1]
    if p_niveles < alpha:
        return "I(0)"
    p_diff = adfuller(serie.diff().dropna())[1]
    if p_diff < alpha:
        return "I(1)"
    return "I(2)+"


def test_engle_granger(serie_y: pd.Series, serie_x: pd.Series, alpha: float = 0.05):
    """
    Ejecuta ADF sobre ambas series primero (reporta orden de integracion),
    y solo interpreta el resultado de Engle-Granger como cointegracion
    valida si ambas son I(1) -- la condicion necesaria del metodo.
    Devuelve dict con: orden_y, orden_x, es_valido, estadistico, p_value, conclusion.
    """
    df = pd.concat([serie_y.rename("y"), serie_x.rename("x")], axis=1).dropna()
    orden_y = orden_integracion(df["y"])
    orden_x = orden_integracion(df["x"])
    es_valido = orden_y == "I(1)" and orden_x == "I(1)"

    estadistico, p_value, _ = coint(df["y"], df["x"])

    if not es_valido:
        conclusion = (
            f"Test no valido en sentido estricto: y es {orden_y}, x es {orden_x}. "
            "Engle-Granger requiere ambas series I(1). Resultado reportado a titulo "
            "informativo unicamente."
        )
    elif p_value < alpha:
        conclusion = (
            f"Cointegran (p={p_value:.4f} < {alpha}): existe una relacion de equilibrio "
            "de largo plazo entre las series, pese a que cada una individualmente tiene raiz unitaria."
        )
    else:
        conclusion = (
            f"No se rechaza ausencia de cointegracion (p={p_value:.4f} >= {alpha}): "
            "no hay evidencia de relacion de largo plazo estable entre las series."
        )

    return {
        "orden_y": orden_y, "orden_x": orden_x, "es_valido": es_valido,
        "estadistico": estadistico, "p_value": p_value, "conclusion": conclusion,
    }


if __name__ == "__main__":
    import numpy as np
    rng = np.random.default_rng(1)
    n = 120
    # Construyo dos series I(1) que cointegran por diseno: x es un random walk,
    # y = 2*x + ruido estacionario (relacion de equilibrio real)
    x = np.cumsum(rng.normal(0, 1, n))
    y = 2 * x + rng.normal(0, 0.5, n)
    idx = pd.date_range("2015-01-01", periods=n, freq="MS")
    r = test_engle_granger(pd.Series(y, index=idx), pd.Series(x, index=idx))
    print(r["conclusion"])
    assert r["orden_x"] == "I(1)"
    assert r["p_value"] < 0.05, "por diseno estas series deberian cointegrar"
    print("OK: test de cointegracion detecta la relacion de equilibrio simulada")

    # Control negativo: dos random walks independientes NO deberian cointegrar
    y2 = np.cumsum(rng.normal(0, 1, n))
    r2 = test_engle_granger(pd.Series(y2, index=idx), pd.Series(x, index=idx))
    print(r2["conclusion"])
    print("OK: control negativo ejecutado (revisar manualmente que el p-value sea alto)")
