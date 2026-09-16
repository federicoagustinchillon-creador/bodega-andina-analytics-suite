# -*- coding: utf-8 -*-
"""
Exporta los resultados del motor econometrico (Analisis_Econometrico) como
tablas curated_gold consumibles por Power BI, y reemplaza la curva Rofex
sintetica (sine-wave, sin sentido economico) por una curva CIP real diaria
2021-2025, calculada con FX real (BCRA A3500) y BADLAR real (BCRA idVariable=7)
-- mismo esquema que el archivo anterior para no romper medidas DAX existentes.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent.parent  # Analisis_Econometrico/
ROOT = BASE.parent
REAL = BASE / "data" / "real"
OUT = BASE / "outputs"
GOLD_02 = ROOT / "03_Inteligencia_Comercial" / "Inteligencia_Comercial.SemanticModel" / "definition" / "tables"
GOLD_ETL = ROOT / "01_Limpieza_de_Datos" / "curated_gold"
GOLD_01_ETL_TARGET = GOLD_ETL  # MercadoCambiario.csv vive aca, project 01 lo importa desde RutaDatos comun


def exportar_elasticidad():
    d = json.load(open(OUT / "elasticidad_resultados.json", encoding="utf-8"))
    filas = []
    for seg, r in d["resultados_por_segmento"].items():
        filas.append({
            "Segmento": seg,
            "Beta_Elasticidad": r.get("beta"),
            "ErrorEstandar": r.get("std_err") or r.get("bse"),
            "PValue": r.get("p_value") or r.get("pvalue"),
            "R2": r.get("r2") or r.get("rsquared"),
            "NObs": r.get("n_obs") or r.get("nobs"),
            "Significativo": bool((r.get("p_value") or r.get("pvalue") or 1) < 0.05),
        })
    df = pd.DataFrame(filas)
    df.to_csv(GOLD_ETL / "ElasticidadSegmento.csv", index=False, encoding="utf-8")
    return df


def exportar_estacionalidad():
    d = json.load(open(OUT / "estacionalidad_resultados.json", encoding="utf-8"))
    tabla = pd.DataFrame(d["tabla_mes_a_mes"])
    tabla.to_csv(GOLD_ETL / "EstacionalidadMensual.csv", index=False, encoding="utf-8")
    return tabla


def exportar_forecast():
    d = json.load(open(OUT / "forecast_resultados.json", encoding="utf-8"))
    real = d["real_12m"]
    fcst = d["forecast_12m"]
    ic = d.get("intervalo_confianza_95") or {}
    fechas_str = sorted(real.keys())
    fechas = pd.to_datetime(fechas_str)
    df = pd.DataFrame({
        "Fecha": fechas.strftime("%Y-%m-%d"),
        "DateKey": fechas.strftime("%Y%m%d").astype(int),
        "VolumenReal": [real[f] for f in fechas_str],
        "VolumenForecast": [fcst[f] for f in fechas_str],
    })
    if ic:
        df["IC95_Inferior"] = [ic[f][0] for f in fechas_str]
        df["IC95_Superior"] = [ic[f][1] for f in fechas_str]
    df.to_csv(GOLD_ETL / "PronosticoDemanda.csv", index=False, encoding="utf-8")

    om = d["orden_modelo"]
    orden_legible = f"SARIMA{tuple(om['order'])}x{tuple(om['seasonal_order'])}" if isinstance(om, dict) and "order" in om else str(om)
    meta = pd.DataFrame([{
        "OrdenModelo": orden_legible, "AIC": d["aic_train"],
        "MAPE": d["MAPE"], "RMSE": d["RMSE"], "NTrain": d["n_train"], "NTest": d["n_test"],
    }])
    meta.to_csv(GOLD_ETL / "PrecisionModelo.csv", index=False, encoding="utf-8")
    return df, meta


NOMBRES_TEST_COINTEGRACION = {
    "test_A_pass_through_cambiario": "Precio Exportacion vs. FX",
    "test_B_pass_through_inflacionario": "Precio Domestico vs. IPC",
}


def exportar_cointegracion():
    d = json.load(open(OUT / "cointegracion_resultados.json", encoding="utf-8"))
    filas = []
    for nombre, r in d.items():
        filas.append({
            "Test": NOMBRES_TEST_COINTEGRACION.get(nombre, nombre),
            "OrdenY": r["orden_y"], "OrdenX": r["orden_x"], "EsValido": bool(r["es_valido"]),
            "Estadistico": r["estadistico"], "PValue": r["p_value"], "Conclusion": r["conclusion"],
        })
    df = pd.DataFrame(filas)
    df.to_csv(GOLD_ETL / "TestsCointegracion.csv", index=False, encoding="utf-8")
    return df


def construir_curva_rofex_diaria_real():
    """Reemplaza MercadoCambiario.csv (antes sine-wave) por CIP real
    diario 2021-2025: spot = FX real BCRA A3500, tasa domestica = BADLAR real BCRA."""
    import sys as _sys
    _sys.path.insert(0, str(BASE / "src"))
    from fx_pricing import forward_teorico, tna_implicita_de_forward

    fx = pd.read_csv(REAL / "bcra_tipo_cambio.csv", parse_dates=["date"]).sort_values("date")
    fx = fx[(fx["date"] >= "2021-01-01") & (fx["date"] <= "2025-12-31")].set_index("date")["value"]

    badlar_raw = json.load(open(REAL / "badlar_p1.json", encoding="utf-8"))["results"][0]["detalle"]
    badlar = pd.Series(
        {pd.Timestamp(x["fecha"]): x["valor"] / 100.0 for x in badlar_raw}
    ).sort_index()
    badlar = badlar.reindex(fx.index, method="ffill").bfill()

    tna_ext = 0.045
    filas = []
    for fecha, spot in fx.items():
        tna_dom = float(badlar.loc[fecha])
        f1m = forward_teorico(spot, tna_dom, tna_ext, 30)
        f3m = forward_teorico(spot, tna_dom, tna_ext, 90)
        filas.append({
            "DateKey": int(fecha.strftime("%Y%m%d")),
            "TipoCambioSpotA3500": round(float(spot), 4),
            "FuturoRofex1M": round(f1m, 4),
            "FuturoRofex3M": round(f3m, 4),
            "DiasVencimiento1M": 30,
            "DiasVencimiento3M": 90,
            "TasaLecapReferenciaTNA": round(tna_dom, 4),
        })
    df = pd.DataFrame(filas)
    df.to_csv(GOLD_ETL / "MercadoCambiario.csv", index=False, encoding="utf-8")
    return df


if __name__ == "__main__":
    e = exportar_elasticidad()
    print("elasticidad:", e.shape)
    s = exportar_estacionalidad()
    print("estacionalidad:", s.shape)
    f, fm = exportar_forecast()
    print("forecast:", f.shape)
    c = exportar_cointegracion()
    print("cointegracion:", c.shape)
    r = construir_curva_rofex_diaria_real()
    print("rofex diario real:", r.shape, r["DateKey"].min(), r["DateKey"].max())
