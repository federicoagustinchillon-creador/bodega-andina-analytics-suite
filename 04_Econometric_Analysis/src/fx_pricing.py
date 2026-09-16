# -*- coding: utf-8 -*-
"""
Paridad de tasas de interes cubierta (Covered Interest Rate Parity, CIP).

Reemplaza la curva de futuros Rofex sintetica (sin fundamento) por un futuro
teorico derivado de: spot real (BCRA) + tasa domestica real (BCRA, LECAP/Badlar)
+ tasa externa de referencia (proxy Fed Funds / SOFR, tipicamente ~0-5% anual).

F = S * (1 + i_dom * d/365) / (1 + i_ext * d/365)

Es la relacion de no-arbitraje estandar de cualquier libro de finanzas
internacionales (Mishkin, Hull) -- el "dolar futuro" en un mercado sin
friccion de capitales debe igualar el spot ajustado por el diferencial de
tasas. Sirve como ancla economica del futuro teorico cuando no hay serie
real de Rofex disponible publicamente.
"""
from dataclasses import dataclass


@dataclass
class CIPResult:
    spot: float
    forward: float
    tna_domestica: float
    tna_externa: float
    dias: int
    tna_implicita: float  # la que "deberia" cotizar el forward, para comparar contra el spread real


def forward_teorico(spot: float, tna_domestica: float, tna_externa: float, dias: int) -> float:
    """Precio forward teorico via CIP. Tasas en TNA (ej. 0.40 = 40% anual)."""
    factor_dom = 1 + tna_domestica * dias / 365
    factor_ext = 1 + tna_externa * dias / 365
    return spot * factor_dom / factor_ext


def tna_implicita_de_forward(spot: float, forward: float, dias: int) -> float:
    """Tasa implicita anualizada que resulta de un spot y un forward dados."""
    if spot <= 0 or dias <= 0:
        return float("nan")
    return (forward / spot - 1) * (365 / dias)


def construir_curva(spot: float, tna_domestica: float, tna_externa: float = 0.045) -> CIPResult:
    """
    Construye el punto de la curva a 90 dias (el tenor usado en el modulo de
    Tesoreria). tna_externa default ~4.5% es un proxy razonable de tasa corta
    en USD (Fed Funds / T-Bill), no una fuente Argentina.
    """
    dias = 90
    fwd = forward_teorico(spot, tna_domestica, tna_externa, dias)
    tna_impl = tna_implicita_de_forward(spot, fwd, dias)
    return CIPResult(
        spot=spot, forward=fwd, tna_domestica=tna_domestica,
        tna_externa=tna_externa, dias=dias, tna_implicita=tna_impl,
    )


if __name__ == "__main__":
    # sanity check con numeros de orden de magnitud realista para ARS 2024
    r = construir_curva(spot=1000.0, tna_domestica=0.45)
    print(r)
    assert r.forward > r.spot, "el forward deberia cotizar con prima si i_dom > i_ext"
    print("OK: forward > spot cuando la tasa domestica excede la externa (logica de no-arbitraje)")
