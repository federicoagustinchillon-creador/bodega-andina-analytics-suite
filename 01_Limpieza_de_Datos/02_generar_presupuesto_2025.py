# -*- coding: utf-8 -*-
"""
Generador de Presupuesto Multianual 2021-2025 Indexado a Inflacion INDEC y Tipo de Cambio BCRA.
Bodega & Agroindustria Andina S.A.
Autor: Federico Agustin Chillon - UNCUYO

El presupuesto de cada anio se fija UNA SOLA VEZ, antes de que ese anio comience, tomando el
precio/costo presupuestado del anio anterior e indexandolo por la inflacion IPC real ya
transcurrida (supuesto de planificacion tipico de un proceso de budgeting), mas un sesgo
estructural fijo por segmento (premium le gana a la inflacion, entrada le pierde). El volumen
presupuestado se ancla al real del mismo mes del anio anterior (preserva estacionalidad) mas un
supuesto de crecimiento por segmento. Ni el precio ni el volumen presupuestados dependen del
dato real del propio mes/anio que se esta presupuestando -- por eso el Real puede desviarse
genuinamente del Plan, que es lo que la pagina de Controller (cascada de margen, variance
Precio/Volumen/Costo) necesita para tener sentido economico.
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GOLD_DIR = os.path.join(BASE_DIR, "curated_gold")
REAL_DIR = os.path.join(os.path.dirname(BASE_DIR), "05_Analisis_Econometrico", "data", "real")


def _drifts_por_segmento(seg, rng):
    """Sesgo estructural de planificacion (fijo por SKU): crecimiento de volumen vs anio
    anterior, y cuanto el precio/costo presupuestado se despega de la pura inflacion."""
    if seg in ["Gran Reserva / Icono", "Reserva"]:
        return rng.normal(0.045, 0.010), rng.normal(0.015, 0.004), rng.normal(0.010, 0.003)
    if seg == "Espumante":
        return rng.normal(0.025, 0.008), rng.normal(0.008, 0.003), rng.normal(0.006, 0.003)
    return rng.normal(-0.005, 0.006), rng.normal(-0.010, 0.004), rng.normal(0.004, 0.003)


def generar_presupuesto_indexado():
    print("--- Generando PresupuestoVentas.csv Multianual 2021-2025 (indexado a IPC real) ---")
    df_v = pd.read_csv(os.path.join(GOLD_DIR, "Ventas.csv"))
    df_prod = pd.read_csv(os.path.join(GOLD_DIR, "Productos.csv"))
    ipc = pd.read_csv(os.path.join(REAL_DIR, "ipc_mensual_2021_2025.csv"))

    df_v["MesDateKey"] = (df_v["DateKey"].astype(str).str[:6] + "01").astype(int)
    df_v["AnioMes"] = df_v["DateKey"].astype(str).str[:4] + "-" + df_v["DateKey"].astype(str).str[4:6]
    df_v["Anio"] = df_v["DateKey"].astype(str).str[:4].astype(int)
    df_v["Mes"] = df_v["DateKey"].astype(str).str[4:6].astype(int)
    df_v["CC_Ppto"] = np.where(df_v["CanalVenta"] == "Exportacion Directa", "CC-203", "CC-202")

    # Inflacion anual IPC (variacion diciembre a diciembre): supuesto de planificacion con el
    # que un area de FP&A real fijaria el presupuesto del anio siguiente.
    ipc["Anio"] = ipc["date"].str[:4].astype(int)
    ipc["Mes"] = ipc["date"].str[5:7].astype(int)
    ipc_dic = ipc[ipc["Mes"] == 12].set_index("Anio")["value"]

    anios = sorted(df_v["Anio"].unique())
    anio_base = anios[0]
    infl_realizada = {
        y: (ipc_dic[y] / ipc_dic[y - 1] - 1)
        for y in anios[1:] if y in ipc_dic.index and (y - 1) in ipc_dic.index
    }
    # El presupuesto de un anio se arma ANTES de que ese anio ocurra: el supuesto de
    # inflacion usado es el de la inflacion YA CONOCIDA del anio anterior (no la de ese
    # mismo anio, que todavia no ocurrio cuando se hizo el presupuesto). Esto es lo que
    # produce desvios genuinos en anios donde la inflacion se acelera o desacelera.
    infl_anual = {anio_base: 0.0}
    for i, y in enumerate(anios[1:], start=1):
        anio_dato_previo = anios[i - 1] if i >= 2 else y
        infl_anual[y] = infl_realizada.get(anio_dato_previo, infl_realizada.get(y, 0.0))

    actual_agg = df_v.groupby(["MesDateKey", "AnioMes", "Anio", "Mes", "ProductoID", "CC_Ppto"], as_index=False).agg(
        VolumenReal=("VolumenReal", "sum"), IngresosReales=("IngresosReales", "sum"), CostoReal=("CostoReal", "sum")
    )
    vol_prev_lookup = actual_agg.set_index(["ProductoID", "CC_Ppto", "Mes", "Anio"])["VolumenReal"].to_dict()

    meses_df = df_v[["MesDateKey", "AnioMes", "Anio", "Mes"]].drop_duplicates().sort_values("MesDateKey")
    prod_list = sorted(df_prod["ProductoID"].unique())
    cc_list = ["CC-202", "CC-203"]

    grid = pd.MultiIndex.from_product([meses_df["MesDateKey"], prod_list, cc_list],
                                       names=["MesDateKey", "ProductoID", "CC_Ppto"]).to_frame(index=False)
    grid = grid.merge(meses_df, on="MesDateKey")
    df_merged = grid.merge(actual_agg, on=["MesDateKey", "AnioMes", "Anio", "Mes", "ProductoID", "CC_Ppto"], how="left")
    df_merged[["VolumenReal", "IngresosReales", "CostoReal"]] = df_merged[["VolumenReal", "IngresosReales", "CostoReal"]].fillna(0)

    seg_map = df_prod.set_index("ProductoID")["Segmento"].to_dict()

    rng = np.random.default_rng(20260917)  # semilla fija para reproducibilidad institucional

    # Sesgo estructural fijo por SKU (una sola vez, no varia mes a mes ni anio a anio)
    sesgos = {pid: _drifts_por_segmento(seg_map.get(pid, "Entrada"), rng) for pid in prod_list}

    # Ancla de precio/costo por SKU y anio: se fija ANTES de que el anio ocurra, a partir del
    # ancla del anio anterior indexada por inflacion real + sesgo estructural del segmento.
    # El catalogo (Productos.PrecioPresupuestadoUnit) es precio VIGENTE HOY, no precio de 2021
    # (esta ~17x por encima del real 2021 por la inflacion ya transcurrida) -- por eso el anio
    # base ancla al precio/costo real promedio DE ESE MISMO ANIO (unico bootstrap necesario,
    # igual que se hace para volumen), y solo a partir de 2022 se indexa por inflacion.
    precio_real_base = actual_agg[actual_agg["Anio"] == anio_base].groupby("ProductoID").apply(
        lambda g: g["IngresosReales"].sum() / g["VolumenReal"].sum() if g["VolumenReal"].sum() > 0 else np.nan
    )
    costo_real_base = actual_agg[actual_agg["Anio"] == anio_base].groupby("ProductoID").apply(
        lambda g: g["CostoReal"].sum() / g["VolumenReal"].sum() if g["VolumenReal"].sum() > 0 else np.nan
    )
    anchor_price = {(pid, anio_base): float(precio_real_base.get(pid, np.nan)) for pid in prod_list}
    anchor_cost = {(pid, anio_base): float(costo_real_base.get(pid, np.nan)) for pid in prod_list}
    for y in anios[1:]:
        infl = infl_anual[y]
        for pid in prod_list:
            _, p_drift, c_drift = sesgos[pid]
            anchor_price[(pid, y)] = anchor_price[(pid, y - 1)] * (1 + infl) * (1 + p_drift)
            anchor_cost[(pid, y)] = anchor_cost[(pid, y - 1)] * (1 + infl) * (1 + c_drift)

    budget_rows = []
    for _, r in df_merged.iterrows():
        dk = int(r["MesDateKey"])
        am = str(r["AnioMes"])
        anio = int(r["Anio"])
        mes = int(r["Mes"])
        pid = str(r["ProductoID"])
        cc = str(r["CC_Ppto"])
        vol_r = float(r["VolumenReal"])

        v_drift, _, _ = sesgos[pid]
        ruido_vol = rng.normal(0, 0.015)
        ruido_px = rng.normal(0, 0.006)

        if anio == anio_base:
            # Anio base: sin anio anterior contra el cual anclar volumen; se usa el propio real
            # con un ruido de planificacion (unico bootstrap necesario, 1 de 5 anios).
            vol_pto = max(0, int(round(vol_r / (1 + ruido_vol)))) if vol_r > 0 else 0
        else:
            vol_prev = vol_prev_lookup.get((pid, cc, mes, anio - 1), 0.0)
            vol_pto = max(0, int(round(vol_prev * (1 + v_drift) * (1 + ruido_vol))))

        px_pto = round(anchor_price[(pid, anio)] * (1 + ruido_px), 2)
        cst_pto = round(anchor_cost[(pid, anio)], 2)

        ing_pto = round(vol_pto * px_pto, 2)
        c_pto = round(vol_pto * cst_pto, 2)
        mb_pto = round(ing_pto - c_pto, 2)

        budget_rows.append({
            "DateKey": dk,
            "AnioMes": am,
            "ProductoID": pid,
            "CentroCostoID": cc,
            "VolumenPresupuestado": vol_pto,
            "PrecioPresupuestadoUnit": px_pto,
            "CostoEstandarUnit": cst_pto,
            "IngresosPresupuestados": ing_pto,
            "CostoPresupuestado": c_pto,
            "MargenBrutoPresupuestado": mb_pto
        })

    df_budget = pd.DataFrame(budget_rows)
    df_budget = df_budget.sort_values(by=["DateKey", "CentroCostoID", "ProductoID"]).reset_index(drop=True)

    out_path = os.path.join(GOLD_DIR, "PresupuestoVentas.csv")
    df_budget.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Archivo guardado en: {out_path}")
    print(f"Total registros: {len(df_budget)} (60 meses x 36 SKUs x 2 CC)")

    # Verificacion anual
    df_v["Year"] = df_v["DateKey"].astype(str).str[:4]
    df_budget["Year"] = df_budget["DateKey"].astype(str).str[:4]
    v_yr = df_v.groupby("Year").agg({"IngresosReales": "sum", "CostoReal": "sum", "MargenBrutoReal": "sum", "VolumenReal": "sum"})
    b_yr = df_budget.groupby("Year").agg({"IngresosPresupuestados": "sum", "CostoPresupuestado": "sum", "MargenBrutoPresupuestado": "sum", "VolumenPresupuestado": "sum"})

    comp = pd.DataFrame({
        "Ventas_ARS_B": (v_yr["IngresosReales"] / 1e9).round(2),
        "Ppto_ARS_B": (b_yr["IngresosPresupuestados"] / 1e9).round(2),
        "Cumpl_Ing_%": (v_yr["IngresosReales"] / b_yr["IngresosPresupuestados"] * 100).round(2),
        "Cumpl_Vol_%": (v_yr["VolumenReal"] / b_yr["VolumenPresupuestado"] * 100).round(2),
        "Margen_Real_%": (v_yr["MargenBrutoReal"] / v_yr["IngresosReales"] * 100).round(2),
        "Margen_Ppto_%": (b_yr["MargenBrutoPresupuestado"] / b_yr["IngresosPresupuestados"] * 100).round(2),
    })
    print("\n=== RESUMEN EJECUTIVO DE CUMPLIMIENTO ANUAL ===")
    print(comp.to_string())

    tot_v_ing = v_yr["IngresosReales"].sum()
    tot_b_ing = b_yr["IngresosPresupuestados"].sum()
    tot_v_vol = v_yr["VolumenReal"].sum()
    tot_b_vol = b_yr["VolumenPresupuestado"].sum()
    print(f"\nTOTAL 5 ANIOS: Cumplimiento Ingresos = {tot_v_ing/tot_b_ing*100:.2f}% | Cumplimiento Volumen = {tot_v_vol/tot_b_vol*100:.2f}%")
    return df_budget


if __name__ == "__main__":
    generar_presupuesto_indexado()
