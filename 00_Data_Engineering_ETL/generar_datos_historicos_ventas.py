# -*- coding: utf-8 -*-
"""
Genera datos crudos (raw) de ventas 2021-2025 para 36 SKUs, calibrados contra
series reales:
- Estacionalidad: indice mensual real de consumo INV mercado interno 2024
  (04_Econometric_Analysis/data/real/indice_estacional_inv_2024.csv)
- Tipo de cambio: BCRA mayorista de referencia mensual 2021-2025 (real, API BCRA)
- Inflacion: IPC INDEC nacional mensual 2021-2025 (real, API series de tiempo)

El precio de exportacion (canal FOB) se fija en USD por segmento y se convierte
a ARS con el FX real del mes -> el pass-through cambiario es un fenomeno real
en los datos, no supuesto. El precio domestico nominal seguir el IPC real mas
una deriva real especifica de segmento (Icono resiliente, Entrada con deterioro
real bajo caida de ingreso), para que el test de cointegracion precio-nominal
vs IPC tenga contenido economico genuino y no trivial (deriva real != 0 en
algunos segmentos => puede no cointegrar 1:1, que es economicamente interesante).
El volumen responde con elasticidad-precio propia por segmento (Entrada mas
elastico que Icono, consistente con bienes de necesidad vs. bienes de lujo).
"""
import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(42)
BASE_DIR = Path(__file__).resolve().parent
REAL_DIR = BASE_DIR.parent / "04_Econometric_Analysis" / "data" / "real"
OUT_DIR = BASE_DIR / "raw"

MESES = pd.date_range("2021-01-01", "2025-12-01", freq="MS")

# ---------------------------------------------------------------- catalogo --
CATALOGO = [
    # (SKU, Descripcion, Varietal, Segmento, FormatoML, CostoBase, PrecioBase)
    ("MAL-CLA-750", "Malbec 750ml", "Malbec", "Entrada", 750, 1900, 4085),
    ("MAL-RES-750", "Malbec Reserva 750ml", "Malbec", "Reserva", 750, 2945, 7557),
    ("MAL-ICO-750", "Malbec Gran Reserva 750ml", "Malbec", "Gran Reserva / Icono", 750, 4940, 14706),
    ("MAL-CLA-1500", "Malbec Magnum 1.5L", "Malbec", "Entrada", 1500, 3800, 8170),
    ("MAL-RES-1500", "Malbec Reserva Magnum 1.5L", "Malbec", "Reserva", 1500, 5890, 15114),
    ("CAF-CLA-750", "Cabernet Franc 750ml", "Cabernet Franc", "Entrada", 750, 2050, 4408),
    ("CAF-RES-750", "Cabernet Franc Reserva 750ml", "Cabernet Franc", "Reserva", 750, 3178, 8154),
    ("CAF-ICO-750", "Cabernet Franc Gran Reserva 750ml", "Cabernet Franc", "Gran Reserva / Icono", 750, 5330, 15867),
    ("CAS-CLA-750", "Cabernet Sauvignon 750ml", "Cabernet Sauvignon", "Entrada", 750, 1950, 4192),
    ("CAS-RES-750", "Cabernet Sauvignon Reserva 750ml", "Cabernet Sauvignon", "Reserva", 750, 3022, 7756),
    ("CAS-ICO-750", "Cabernet Sauvignon Gran Reserva 750ml", "Cabernet Sauvignon", "Gran Reserva / Icono", 750, 5070, 15093),
    ("BON-CLA-750", "Bonarda 750ml", "Bonarda", "Entrada", 750, 1550, 3332),
    ("BON-RES-750", "Bonarda Reserva 750ml", "Bonarda", "Reserva", 750, 2402, 6165),
    ("SYR-CLA-750", "Syrah 750ml", "Syrah", "Entrada", 750, 1900, 4085),
    ("SYR-RES-750", "Syrah Reserva 750ml", "Syrah", "Reserva", 750, 2945, 7557),
    ("MER-CLA-750", "Merlot 750ml", "Merlot", "Entrada", 750, 1850, 3978),
    ("MER-RES-750", "Merlot Reserva 750ml", "Merlot", "Reserva", 750, 2868, 7358),
    ("BLC-CLA-750", "Blend Corte Bordeles 750ml", "Blend Corte Bordeles", "Entrada", 750, 2400, 5160),
    ("BLC-RES-750", "Blend Corte Bordeles Reserva 750ml", "Blend Corte Bordeles", "Reserva", 750, 3720, 9546),
    ("BLC-ICO-750", "Blend Corte Bordeles Gran Reserva 750ml", "Blend Corte Bordeles", "Gran Reserva / Icono", 750, 6240, 18576),
    ("CHA-CLA-750", "Chardonnay 750ml", "Chardonnay", "Entrada", 750, 1750, 3762),
    ("CHA-RES-750", "Chardonnay Reserva 750ml", "Chardonnay", "Reserva", 750, 2712, 6961),
    ("SAB-CLA-750", "Sauvignon Blanc 750ml", "Sauvignon Blanc", "Entrada", 750, 1650, 3548),
    ("SAB-RES-750", "Sauvignon Blanc Reserva 750ml", "Sauvignon Blanc", "Reserva", 750, 2558, 6563),
    ("TOR-CLA-750", "Torrontes 750ml", "Torrontes", "Entrada", 750, 1500, 3225),
    ("TOR-RES-750", "Torrontes Reserva 750ml", "Torrontes", "Reserva", 750, 2325, 5966),
    ("PIN-CLA-750", "Pinot Noir 750ml", "Pinot Noir", "Entrada", 750, 2300, 4945),
    ("PIN-RES-750", "Pinot Noir Reserva 750ml", "Pinot Noir", "Reserva", 750, 3565, 9148),
    ("ROS-CLA-750", "Rose de Malbec 750ml", "Rose de Malbec", "Entrada", 750, 1700, 3655),
    ("ROS-RES-750", "Rose de Malbec Reserva 750ml", "Rose de Malbec", "Reserva", 750, 2635, 6762),
    ("CHA-ESP-750", "Chardonnay Extra Brut 750ml", "Chardonnay Extra Brut", "Espumante", 750, 3060, 8127),
    ("ROS-ESP-750", "Rose Brut 750ml", "Rose Brut", "Espumante", 750, 3060, 8127),
    ("MAL-ESP-750", "Malbec Brut Nature 750ml", "Malbec Brut Nature", "Espumante", 750, 3060, 8127),
    ("MAL-BIB-3000", "Bag in Box Malbec 3L", "Malbec", "Granel / Masivo", 3000, 4940, 11438),
    ("BON-BIB-3000", "Bag in Box Bonarda 3L", "Bonarda", "Granel / Masivo", 3000, 4940, 11438),
    ("BLT-BIB-3000", "Bag in Box Blend Tinto 3L", "Blend Tinto", "Granel / Masivo", 3000, 4420, 10234),
]
assert len(CATALOGO) == 36

SEGMENTO_PARAMS = {
    # beta: elasticidad-precio propia | deriva_real: %anual de crecimiento del
    # precio domestico POR ENCIMA de IPC | pct_fob: prob. de que una transaccion
    # sea de exportacion | usd_min/usd_max: precio FOB en USD/unidad 750ml equiv.
    "Entrada":               dict(beta=-1.25, deriva_real=-0.015, pct_fob=0.08, usd=(3.0, 5.0)),
    "Reserva":                dict(beta=-0.85, deriva_real=0.00,  pct_fob=0.32, usd=(6.0, 10.0)),
    "Gran Reserva / Icono":   dict(beta=-0.45, deriva_real=0.02,  pct_fob=0.55, usd=(15.0, 30.0)),
    "Espumante":              dict(beta=-0.95, deriva_real=-0.005, pct_fob=0.20, usd=(7.0, 12.0)),
    "Granel / Masivo":        dict(beta=-1.6, deriva_real=-0.02,  pct_fob=0.04, usd=(0.9, 1.4)),  # USD/litro
}

TENDENCIA_ANUAL_DOMESTICA = -0.02   # consumo interno en caida secular (real, ver INV)
TENDENCIA_ANUAL_EXPORT = 0.015      # exportaciones levemente crecientes


def cargar_series_reales():
    fx = pd.read_csv(REAL_DIR / "fx_mensual_2021_2025.csv", parse_dates=["date"], index_col="date")["value"]
    ipc = pd.read_csv(REAL_DIR / "ipc_mensual_2021_2025.csv", parse_dates=["date"], index_col="date")["value"]
    idx_est = pd.read_csv(REAL_DIR / "indice_estacional_inv_2024.csv", index_col="mes")["indice_estacional_2024_real"]
    fx = fx.reindex(MESES).ffill().bfill()
    ipc = ipc.reindex(MESES).ffill().bfill()
    return fx, ipc, idx_est


def sucio_fecha(fecha, i):
    """Reproduce la mezcla de formatos de fecha del archivo raw original."""
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"]
    fmt = formatos[i % len(formatos)]
    return fecha.strftime(fmt)


def sucio_texto(v, i):
    """Ensucia levemente MATNR/INCO1 (case + espacios) como el archivo original."""
    if i % 11 == 0:
        return f" {v.lower()} "
    if i % 7 == 0:
        return v.lower()
    if i % 13 == 0:
        return f"{v} "
    return v


def generar():
    fx, ipc, idx_est = cargar_series_reales()
    ipc_base = ipc.iloc[0]

    filas = []
    vbeln = 90001001
    n_cli = 1000

    for i, (sku, desc, varietal, segmento, formato, costo0, precio0) in enumerate(CATALOGO, start=1):
        producto_id = f"PRD-{i:02d}"
        p = SEGMENTO_PARAMS[segmento]
        es_granel_litro = segmento == "Granel / Masivo"
        vol_base_mes = RNG.integers(9, 20)  # cantidad de transacciones/mes para este SKU

        for t, fecha_mes in enumerate(MESES):
            anio_frac = t / 12
            mes_cal = fecha_mes.month

            # --- precio domestico nominal: IPC real + deriva real de segmento
            precio_dom = precio0 * (ipc.iloc[t] / ipc_base) * ((1 + p["deriva_real"]) ** anio_frac)
            precio_dom *= 1 + RNG.normal(0, 0.02)

            # --- precio export (FOB) en ARS: USD fijo * FX real del mes
            usd_lo, usd_hi = p["usd"]
            precio_usd = RNG.uniform(usd_lo, usd_hi) * (1 if es_granel_litro else 1)
            precio_fob_ars = precio_usd * fx.iloc[t] * (formato / 750 if not es_granel_litro else 1)

            # --- volumen: estacionalidad real + tendencia + respuesta a precio real
            precio_real_rel = (precio_dom / (ipc.iloc[t] / ipc_base)) / precio0
            resp_precio = precio_real_rel ** p["beta"]
            estacional = idx_est.loc[mes_cal]
            tendencia = (1 + TENDENCIA_ANUAL_DOMESTICA) ** anio_frac
            vol_medio = vol_base_mes * estacional * tendencia * resp_precio
            vol_medio = max(vol_medio, 1.5)

            n_txn = max(1, RNG.poisson(vol_medio))
            for j in range(n_txn):
                es_fob = RNG.random() < p["pct_fob"] * ((1 + TENDENCIA_ANUAL_EXPORT) ** anio_frac)
                dia = int(RNG.integers(1, 28))
                fecha_txn = fecha_mes.replace(day=dia)

                cantidad = int(RNG.integers(20, 260))
                if es_fob:
                    precio_unit = precio_fob_ars
                    canal = RNG.choice(["FOB"])
                    vkbur = "CC-203"
                else:
                    precio_unit = precio_dom
                    canal = RNG.choice(["RETAIL", "HORECA", "DIST"], p=[0.45, 0.30, 0.25])
                    vkbur = RNG.choice(["CC-101", "CC-202"])

                netwr = cantidad * precio_unit * (1 + RNG.normal(0, 0.03))
                costo_unit = costo0 * (ipc.iloc[t] / ipc_base) * (1 + RNG.normal(0, 0.02))
                wavwr = cantidad * costo_unit

                idx_row = len(filas)
                filas.append({
                    "VBELN": vbeln,
                    "FKDAT": sucio_fecha(fecha_txn, idx_row),
                    "MATNR": sucio_texto(producto_id, idx_row),
                    "KUNNR": f"CLI-{1000 + int(RNG.integers(0, n_cli))}",
                    "FKIMG": cantidad,
                    "NETWR": round(netwr, 2),
                    "WAVWR": round(wavwr, 2),
                    "VKBUR": sucio_texto(vkbur, idx_row),
                    "INCO1": sucio_texto(canal, idx_row),
                })
                vbeln += 1

    df = pd.DataFrame(filas)
    df = df.sample(frac=1, random_state=7).reset_index(drop=True)  # desordenar como iria llegando de SAP
    return df


def generar_maestro_productos():
    filas = []
    for i, (sku, desc, varietal, segmento, formato, costo0, precio0) in enumerate(CATALOGO, start=1):
        filas.append({
            "ProductoID": f"PRD-{i:02d}",
            "SKU": sku,
            "Descripcion": desc,
            "Linea": {
                "Entrada": "Entrada / Volumen",
                "Reserva": "Alta Gama",
                "Gran Reserva / Icono": "Icono / Super Premium",
                "Espumante": "Espumantes",
                "Granel / Masivo": "Granel / Masivo",
            }[segmento],
            "Segmento": segmento,
            "Varietal": varietal,
            "FormatoML": formato,
            "CostoEstandarUnit": float(costo0),
            "PrecioPresupuestadoUnit": float(precio0),
        })
    return pd.DataFrame(filas)


if __name__ == "__main__":
    maestro = generar_maestro_productos()
    maestro.to_csv(OUT_DIR / "raw_maestro_productos.csv", index=False)
    print(f"raw_maestro_productos.csv: {maestro.shape[0]} SKUs")

    ventas = generar()
    ventas.to_csv(OUT_DIR / "raw_sap_vbrk_vbrp_ventas.csv", index=False)
    print(f"raw_sap_vbrk_vbrp_ventas.csv: {ventas.shape[0]} filas, "
          f"{ventas['FKDAT'].str.slice(0, 4).nunique()} formatos de fecha mixtos")

    # sanity checks rapidos
    ventas["MATNR_norm"] = ventas["MATNR"].str.strip().str.upper()
    print("SKUs distintos en ventas:", ventas["MATNR_norm"].nunique(), "(esperado 36)")
    print("Canales:", ventas["INCO1"].str.strip().str.upper().value_counts().to_dict())
