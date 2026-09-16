# -*- coding: utf-8 -*-
"""
Construccion de la curva Rofex teorica HISTORICA (60 meses, 2021-01 a 2025-12)
via Paridad de Tasas de Interes Cubierta (CIP), mes a mes.

Fuentes de datos REALES (no inventadas):
- Spot ARS/USD mensual: data/real/fx_mensual_2021_2025.csv
  (BCRA, tipo de cambio mayorista de referencia, promedio mensual)
- Tasa domestica (TNA) mensual: data/real/badlar_mensual_2021_2025.csv
  (BCRA API v4.0 Monetarias, idVariable=7 "Tasa de interes BADLAR de
  bancos privados", https://api.bcra.gob.ar/estadisticas/v4.0/Monetarias/7,
  promedio mensual de las observaciones diarias, TNA expresada en decimal)

Por que BADLAR y no "Tasa de Politica Monetaria" (idVariable=160/161):
la serie de Tasa de Politica Monetaria del BCRA solo cubre 2021-01-04 a
2025-07-10 (el BCRA discontinuo esa tasa como ancla de politica monetaria
a mediados de 2025). BADLAR (idVariable=7) tiene cobertura diaria completa
y sin huecos para los 60 meses del periodo 2021-01 a 2025-12 (verificado:
1215 observaciones diarias, min=2021-01-04, max=2025-12-30), por lo que es
la serie real de mayor cobertura temporal disponible para este ejercicio.
No se uso ningun proxy/valor fabricado: los 60 meses de tna_domestica
provienen de datos reales descargados de la API del BCRA.

- Tasa externa: se mantiene el default de construir_curva() (4.5%, proxy de
  tasa corta en USD / Fed Funds, ya documentado en fx_pricing.py) para los
  60 meses, tal como pide la consigna.

Este script es reusable: build_curva_historica() puede importarse desde el
notebook final y volver a correrse sin tocar nada a mano.
"""
from __future__ import annotations

import csv
import statistics
from dataclasses import asdict
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fx_pricing import construir_curva  # noqa: E402

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "real"
OUTPUT_DIR = BASE_DIR / "outputs"

FX_CSV = DATA_DIR / "fx_mensual_2021_2025.csv"
BADLAR_CSV = DATA_DIR / "badlar_mensual_2021_2025.csv"
OUTPUT_CSV = OUTPUT_DIR / "curva_rofex_teorica_2021_2025.csv"

TNA_EXTERNA_DEFAULT = 0.045  # ver docstring de construir_curva() en fx_pricing.py


def _leer_serie_mensual(path: Path) -> dict[str, float]:
    """Lee un CSV de 2 columnas (date, value) a un dict {'YYYY-MM-DD': float}."""
    serie: dict[str, float] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames or []
        value_col = cols[1]
        for row in reader:
            serie[row["date"]] = float(row[value_col])
    return serie


def build_curva_historica(
    fx_csv: Path = FX_CSV,
    badlar_csv: Path = BADLAR_CSV,
    tna_externa: float = TNA_EXTERNA_DEFAULT,
) -> list[dict]:
    """
    Construye la curva Rofex teorica (forward a 90 dias via CIP) para cada
    mes disponible en la interseccion de fx_csv y badlar_csv.

    Retorna una lista de dicts, uno por mes, con las columnas de salida.
    """
    spot_mensual = _leer_serie_mensual(fx_csv)
    tna_mensual = _leer_serie_mensual(badlar_csv)

    fechas_comunes = sorted(set(spot_mensual) & set(tna_mensual))
    if not fechas_comunes:
        raise ValueError("Sin fechas en comun entre spot y tasa domestica.")

    filas = []
    for fecha in fechas_comunes:
        spot = spot_mensual[fecha]
        tna_dom = tna_mensual[fecha]
        resultado = construir_curva(spot=spot, tna_domestica=tna_dom, tna_externa=tna_externa)
        filas.append(
            {
                "fecha": fecha,
                "spot_ars_usd": resultado.spot,
                "tna_domestica_usada": resultado.tna_domestica,
                "tna_externa_usada": resultado.tna_externa,
                "forward_teorico_90d": resultado.forward,
                "tna_implicita_forward": resultado.tna_implicita,
            }
        )
    return filas


def guardar_csv(filas: list[dict], output_csv: Path = OUTPUT_CSV) -> Path:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    columnas = [
        "fecha",
        "spot_ars_usd",
        "tna_domestica_usada",
        "tna_externa_usada",
        "forward_teorico_90d",
        "tna_implicita_forward",
    ]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()
        for fila in filas:
            writer.writerow(fila)
    return output_csv


def _correlacion(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2:
        return float("nan")
    try:
        return statistics.correlation(xs, ys)
    except statistics.StatisticsError:
        return float("nan")


def imprimir_resumen(filas: list[dict]) -> None:
    fechas = [f["fecha"] for f in filas]
    spots = [f["spot_ars_usd"] for f in filas]
    tna_impl = [f["tna_implicita_forward"] for f in filas]
    forwards = [f["forward_teorico_90d"] for f in filas]

    corr = _correlacion(spots, forwards)

    print("=== Resumen curva Rofex teorica historica (CIP) ===")
    print(f"Meses: {len(filas)}  |  Rango: {fechas[0]} a {fechas[-1]}")
    print(f"Spot ARS/USD: min={min(spots):.2f}  max={max(spots):.2f}")
    print(
        "TNA implicita del forward: "
        f"min={min(tna_impl):.4f}  max={max(tna_impl):.4f}  "
        f"promedio={statistics.mean(tna_impl):.4f}"
    )
    veredicto = "OK: forward sigue al spot razonablemente" if corr > 0.95 else (
        "ALERTA: forward y spot divergen mas de lo esperado"
    )
    print(f"Correlacion spot vs forward_teorico_90d: {corr:.6f} -> {veredicto}")


if __name__ == "__main__":
    filas = build_curva_historica()
    ruta = guardar_csv(filas)
    print(f"CSV guardado en: {ruta}")
    imprimir_resumen(filas)
