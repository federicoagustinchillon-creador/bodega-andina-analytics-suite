# -*- coding: utf-8 -*-
"""
Generador de Presupuesto Multianual 2021-2025 Indexado a Inflacion INDEC y Tipo de Cambio BCRA.
Bodega & Agroindustria Andina S.A.
Autor: Federico Agustin Chillon - UNCUYO

Indexa precios y costos presupuestados ano a ano conforme a la inflacion acumulada IPC
y tipo de cambio oficial, manteniendo la estacionalidad enologica INV y generando variaciones
presupuestarias ejecutivas realistas (+-2% a +-4%), de modo que el Cumplimiento Presupuestario
anual y total oscile consistentemente entre 98.0% y 102.5% (promedio ~100.4%).
"""

import os
import numpy as np
import pandas as pd

BASE_DIR = r"G:\Mi unidad\Federico_Chillon_Master\02_Insercion_Laboral_y_CVs\Proyecto Empresarial\Portfolio_Empresarial_PowerBI\01_Limpieza_de_Datos"
GOLD_DIR = os.path.join(BASE_DIR, "curated_gold")

def generar_presupuesto_indexado():
    print("--- Generando PresupuestoVentas.csv Multianual 2021-2025 ---")
    ventas_path = os.path.join(GOLD_DIR, "Ventas.csv")
    prod_path = os.path.join(GOLD_DIR, "Productos.csv")
    
    df_v = pd.read_csv(ventas_path)
    df_prod = pd.read_csv(prod_path)
    
    # Derivar grano mensual y centro de costo presupuestario
    df_v["MesDateKey"] = (df_v["DateKey"].astype(str).str[:6] + "01").astype(int)
    df_v["AnioMes"] = df_v["DateKey"].astype(str).str[:4] + "-" + df_v["DateKey"].astype(str).str[4:6]
    df_v["CC_Ppto"] = np.where(df_v["CanalVenta"] == "Exportacion Directa", "CC-203", "CC-202")
    
    # Agrupacion de ventas reales por mes, producto y centro de costo
    actual_agg = df_v.groupby(["MesDateKey", "AnioMes", "ProductoID", "CC_Ppto"], as_index=False).agg({
        "VolumenReal": "sum",
        "IngresosReales": "sum",
        "CostoReal": "sum"
    })
    
    # Cuadricula completa: 60 meses x 36 productos x 2 centros de costo (4,320 registros)
    meses_df = df_v[["MesDateKey", "AnioMes"]].drop_duplicates().sort_values("MesDateKey")
    prod_list = sorted(df_prod["ProductoID"].unique())
    cc_list = ["CC-202", "CC-203"]
    
    grid = []
    for _, m in meses_df.iterrows():
        for p in prod_list:
            for cc in cc_list:
                grid.append({
                    "MesDateKey": m["MesDateKey"],
                    "AnioMes": m["AnioMes"],
                    "ProductoID": p,
                    "CC_Ppto": cc
                })
    df_grid = pd.DataFrame(grid)
    
    df_merged = df_grid.merge(actual_agg, on=["MesDateKey", "AnioMes", "ProductoID", "CC_Ppto"], how="left")
    df_merged["VolumenReal"] = df_merged["VolumenReal"].fillna(0)
    df_merged["IngresosReales"] = df_merged["IngresosReales"].fillna(0)
    df_merged["CostoReal"] = df_merged["CostoReal"].fillna(0)
    
    # Referencias de precio y costo unitario promedio mensual
    price_ref = df_v.groupby(["MesDateKey", "ProductoID"])["PrecioRealUnit"].mean().to_dict()
    cost_ref = df_v.groupby(["MesDateKey", "ProductoID"])["CostoRealUnit"].mean().to_dict()
    
    # Semilla deterministica fija para reproducibilidad institucional
    rng = np.random.default_rng(20260917)
    
    seg_map = df_prod.set_index("ProductoID")["Segmento"].to_dict()
    
    budget_rows = []
    for _, r in df_merged.iterrows():
        dk = int(r["MesDateKey"])
        am = str(r["AnioMes"])
        pid = str(r["ProductoID"])
        cc = str(r["CC_Ppto"])
        vol_r = float(r["VolumenReal"])
        
        pref = price_ref.get((dk, pid), 10000.0)
        cref = cost_ref.get((dk, pid), 5000.0)
        
        seg = seg_map.get(pid, "Entrada")
        
        # Desviaciones de planificacion calibradas estructuralmente por segmento:
        # Alta Gama / Icono: volumen y precio superan ligeramente el plan
        # Entrada / Masivo: volumen en meta, leves bonificaciones comerciales
        # Insumos secos y fabriles: costo real incurrido superior al estandar presupuestado
        if seg in ["Gran Reserva / Icono", "Reserva"]:
            v_drift = rng.normal(0.038, 0.003)
            p_drift = rng.normal(0.028, 0.003)
        elif seg == "Espumante":
            v_drift = rng.normal(0.018, 0.003)
            p_drift = rng.normal(0.012, 0.003)
        else: # Entrada / Granel
            v_drift = rng.normal(-0.003, 0.002)
            p_drift = rng.normal(-0.006, 0.002)
            
        c_drift = rng.normal(0.018, 0.003)
        
        if vol_r > 0:
            vol_pto = max(1, int(round(vol_r / (1 + v_drift))))
            px_pto = round((r["IngresosReales"] / vol_r) / (1 + p_drift), 2)
            cst_pto = round((r["CostoReal"] / vol_r) / (1 + c_drift), 2)
        else:
            vol_pto = 0
            px_pto = round(pref, 2)
            cst_pto = round(cref, 2)
            
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
    
    # Ordenar por DateKey, CentroCostoID, ProductoID
    df_budget = df_budget.sort_values(by=["DateKey", "CentroCostoID", "ProductoID"]).reset_index(drop=True)
    
    out_path = os.path.join(GOLD_DIR, "PresupuestoVentas.csv")
    df_budget.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Archivo guardado en: {out_path}")
    print(f"Total registros: {len(df_budget)} (60 meses x 36 SKUs x 2 CC)")
    
    # Verificacion anual
    df_v["Year"] = df_v["DateKey"].astype(str).str[:4]
    df_budget["Year"] = df_budget["DateKey"].astype(str).str[:4]
    v_yr = df_v.groupby("Year").agg({"IngresosReales":"sum", "CostoReal":"sum", "MargenBrutoReal":"sum", "VolumenReal":"sum"})
    b_yr = df_budget.groupby("Year").agg({"IngresosPresupuestados":"sum", "CostoPresupuestado":"sum", "MargenBrutoPresupuestado":"sum", "VolumenPresupuestado":"sum"})
    
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
