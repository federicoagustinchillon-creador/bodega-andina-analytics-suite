# -*- coding: utf-8 -*-
"""
Script de Actualizacion de Capa de Datos y Modelos Semanticos
Bodega & Agroindustria Andina S.A.
Autor: Federico Agustin Chillon - UNCUYO
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = r"c:\Users\fedea\Downloads\cv\Portfolio_Empresarial_PowerBI"
GOLD_DIR = os.path.join(BASE_DIR, "00_Data_Engineering_ETL", "curated_gold")
RAW_DIR = os.path.join(BASE_DIR, "00_Data_Engineering_ETL", "raw")

def update_fact_operaciones_planta():
    print("--- Actualizando fact_operaciones_planta.csv ---")
    p = os.path.join(GOLD_DIR, "fact_operaciones_planta.csv")
    df = pd.read_csv(p, encoding="latin1") # Read robustly to repair any encoding damage

    # Mapa exacto de coordenadas y nombres estandarizados de Mendoza
    geo_info = {
        "Finca Agrelo": (-33.1250, -68.8950, "Agrelo, Luján de Cuyo, Mendoza, Argentina"),
        "Finca Barrancas": (-33.0560, -68.7050, "Barrancas, Maipú, Mendoza, Argentina"),
        "Finca Gualtallary": (-33.3850, -69.2150, "Gualtallary, Tupungato, Mendoza, Argentina"),
        "Finca Altamira": (-33.7750, -69.1550, "Paraje Altamira, San Carlos, Mendoza, Argentina"),
    }

    df["FincaOrigen"] = df["FincaOrigen"].str.strip()
    df["Latitud"] = df["FincaOrigen"].map(lambda x: geo_info[x][0]).round(4)
    df["Longitud"] = df["FincaOrigen"].map(lambda x: geo_info[x][1]).round(4)
    df["UbicacionGeografica"] = df["FincaOrigen"].map(lambda x: geo_info[x][2])

    # Asegurar sanidad limpia
    df["CalificacionSanitaria"] = df["CalificacionSanitaria"].str.strip()

    # Reordenar columnas
    cols = [
        "RemitoID", "DateKey", "Fecha", "CentroCostoID", "VariedadUva",
        "FincaOrigen", "KilosEntrada", "GradosBrix", "LitrosMostoObtenido",
        "RendimientoExtraccionPct", "CalificacionSanitaria", "UbicacionGeografica",
        "Latitud", "Longitud"
    ]
    df = df[cols]

    # Guardar en UTF-8 limpio
    df.to_csv(p, index=False, encoding="utf-8")
    print(f"fact_operaciones_planta.csv actualizado con {len(df)} registros y columnas Latitud/Longitud.")
    return df

def create_fact_inventario_guarda():
    print("\n--- Creando fact_inventario_guarda.csv ---")
    p = os.path.join(GOLD_DIR, "fact_inventario_guarda.csv")

    meses = [
        ("20250101", "2025-01", 1.00),
        ("20250201", "2025-02", 1.08), # Vendimia inicia
        ("20250301", "2025-03", 1.25), # Pico molienda vendimia
        ("20250401", "2025-04", 1.20), # Fin molienda
        ("20250501", "2025-05", 1.15), # Trasiego a barricas
        ("20250601", "2025-06", 1.12), # Crianza activa invierno
        ("20250701", "2025-07", 1.10), # Estabilizacion
        ("20250801", "2025-08", 1.06), # Inicio fraccionamiento
        ("20250901", "2025-09", 1.04), # Embotellado
        ("20251001", "2025-10", 1.02), # Estiba en botella
        ("20251101", "2025-11", 0.98), # Despachos de fin de anio
        ("20251201", "2025-12", 0.94)  # Despachos navidenos / vaciado estiba
    ]

    # Parametros base diferenciados por SKU y TipoVasija
    # SKU Profiles:
    # PRD-01: Malbec Reserva 750ml (Alta Gama)
    # PRD-02: Cabernet Franc Reserva 750ml (Alta Gama)
    # PRD-03: Malbec Clasico 750ml (Entrada / Volumen)
    # PRD-04: Chardonnay Extra Brut 750ml (Espumantes)
    # PRD-05: Bag in Box Malbec 3L (Granel / Masivo)
    
    vasijas = [
        "Piletas de Acero Inoxidable",
        "Barricas de Roble Frances",
        "Barricas de Roble Americano",
        "Botellero en Estiba Climatizada"
    ]

    # Definicion de matrices base (LitrosBase, ValorBaseUnitario, MermaBasePct, DIOBase, Calidad)
    base_profiles = {
        ("PRD-01", "Piletas de Acero Inoxidable"): (18000, 480.0, 0.0080, 60.0, "Estabilizado"),
        ("PRD-01", "Barricas de Roble Frances"): (48000, 750.0, 0.0340, 330.0, "En Crianza"),
        ("PRD-01", "Barricas de Roble Americano"): (30000, 620.0, 0.0310, 270.0, "En Crianza"),
        ("PRD-01", "Botellero en Estiba Climatizada"): (22000, 720.0, 0.0020, 150.0, "Optimo"),

        ("PRD-02", "Piletas de Acero Inoxidable"): (15000, 510.0, 0.0075, 65.0, "Estabilizado"),
        ("PRD-02", "Barricas de Roble Frances"): (38000, 780.0, 0.0360, 350.0, "En Crianza"),
        ("PRD-02", "Barricas de Roble Americano"): (20000, 640.0, 0.0320, 280.0, "En Crianza"),
        ("PRD-02", "Botellero en Estiba Climatizada"): (16000, 760.0, 0.0022, 160.0, "Optimo"),

        ("PRD-03", "Piletas de Acero Inoxidable"): (140000, 165.0, 0.0090, 75.0, "Aprobado Enologia"),
        ("PRD-03", "Barricas de Roble Frances"): (12000, 360.0, 0.0290, 160.0, "En Crianza"),
        ("PRD-03", "Barricas de Roble Americano"): (40000, 260.0, 0.0260, 140.0, "En Crianza"),
        ("PRD-03", "Botellero en Estiba Climatizada"): (30000, 250.0, 0.0025, 75.0, "Aprobado Enologia"),

        ("PRD-04", "Piletas de Acero Inoxidable"): (35000, 340.0, 0.0085, 90.0, "Estabilizado"),
        ("PRD-04", "Barricas de Roble Frances"): (10000, 560.0, 0.0280, 180.0, "En Crianza"),
        ("PRD-04", "Barricas de Roble Americano"): (3000, 420.0, 0.0250, 130.0, "En Crianza"),
        ("PRD-04", "Botellero en Estiba Climatizada"): (22000, 520.0, 0.0015, 220.0, "Optimo"),

        ("PRD-05", "Piletas de Acero Inoxidable"): (220000, 75.0, 0.0070, 45.0, "Aprobado Enologia"),
        ("PRD-05", "Barricas de Roble Frances"): (3000, 180.0, 0.0270, 95.0, "En Crianza"),
        ("PRD-05", "Barricas de Roble Americano"): (12000, 130.0, 0.0240, 75.0, "En Crianza"),
        ("PRD-05", "Botellero en Estiba Climatizada"): (38000, 95.0, 0.0012, 35.0, "Aprobado Enologia"),
    }

    # Fijar semilla deterministica para reproducibilidad perfecta
    np.random.seed(42)

    rows = []
    for date_key, anio_mes, factor_estac in meses:
        m_num = int(anio_mes.split("-")[1])
        for (prd_id, vasija), (litros_base, val_unit_base, merma_base, dio_base, calidad_base) in base_profiles.items():
            # Modulacion estacional segun tipo de vasija
            if vasija == "Piletas de Acero Inoxidable":
                # Acero sube fuertemente en vendimia (meses 2-4)
                estac_litros = factor_estac * (1.15 if m_num in [2, 3, 4] else 0.95)
            elif "Roble" in vasija:
                # Roble sube post vendimia (meses 5-8) y baja ligeramente por evaporacion/trasiego
                estac_litros = factor_estac * (1.08 if m_num in [5, 6, 7, 8] else 0.98)
            else: # Botellero en estiba
                # Estiba sube en embotellado (meses 8-10) y baja en ventas fin de anio (11-12)
                estac_litros = factor_estac * (1.18 if m_num in [9, 10] else (0.85 if m_num in [11, 12] else 0.96))

            noise_litros = 1.0 + np.random.uniform(-0.025, 0.025)
            litros = round(litros_base * estac_litros * noise_litros, 1)

            noise_val = 1.0 + np.random.uniform(-0.015, 0.015)
            # A medida que avanza el anio, el valor en guarda gana valor por crianza (costo absorbido)
            crianza_val_factor = 1.0 + (m_num * 0.008)
            val_unit = val_unit_base * crianza_val_factor * noise_val
            valor_inv = round(litros * val_unit, 2)

            noise_merma = 1.0 + np.random.uniform(-0.04, 0.04)
            # Merma es mayor en meses calidos (dic, ene, feb, mar) en barricas
            temp_merma_factor = 1.12 if m_num in [12, 1, 2, 3] and "Roble" in vasija else 1.0
            merma_pct = round(merma_base * temp_merma_factor * noise_merma, 4)

            noise_dio = 1.0 + np.random.uniform(-0.03, 0.03)
            dio_dias = round(dio_base * noise_dio, 1)

            # Estado de calidad dinamico segun madurez
            if vasija == "Botellero en Estiba Climatizada":
                calidad = "Optimo" if m_num >= 8 else "Estiba Fina"
            elif "Roble" in vasija:
                calidad = "Optimo" if (m_num >= 9 and "Frances" in vasija) else "En Crianza"
            else:
                calidad = "Aprobado Enologia" if prd_id in ["PRD-03", "PRD-05"] else "Estabilizado"

            rows.append({
                "DateKey": int(date_key),
                "AnioMes": anio_mes,
                "ProductoID": prd_id,
                "TipoVasija": vasija,
                "Litros": litros,
                "ValorInventario": valor_inv,
                "MermaPct": merma_pct,
                "DIODias": dio_dias,
                "EstadoCalidad": calidad
            })

    df_inv = pd.DataFrame(rows)
    df_inv.to_csv(p, index=False, encoding="utf-8")
    print(f"fact_inventario_guarda.csv creado exitosamente con {len(df_inv)} registros (12 meses x 5 SKUs x 4 vasijas).")
    print("Resumen por ProductoID:")
    print(df_inv.groupby("ProductoID")[["Litros", "ValorInventario", "MermaPct", "DIODias"]].mean().round(2))
    print("\nResumen por TipoVasija:")
    print(df_inv.groupby("TipoVasija")[["Litros", "ValorInventario", "MermaPct", "DIODias"]].mean().round(2))
    return df_inv

def update_dim_cuentas_contables():
    print("\n--- Actualizando dim_cuentas_contables.csv ---")
    p = os.path.join(GOLD_DIR, "dim_cuentas_contables.csv")
    df_cta = pd.read_csv(p, encoding="utf-8")

    # Definir cuentas industriales requeridas
    industrial_accounts = [
        {"CuentaID": "CTA-201", "NombreCuenta": "Materia Prima Uva & Mosto", "Naturaleza": "Costos", "Rubro": "COGS"},
        {"CuentaID": "CTA-202", "NombreCuenta": "Insumos Secos (Botellas, Corchos, Capsulas, Cajas)", "Naturaleza": "Costos", "Rubro": "COGS"},
        {"CuentaID": "CTA-203", "NombreCuenta": "Mano de Obra Directa de Bodega", "Naturaleza": "Costos", "Rubro": "COGS"},
        {"CuentaID": "CTA-204", "NombreCuenta": "Costos Indirectos Fabriles (Energia, Gas, Mantenimiento)", "Naturaleza": "Costos", "Rubro": "COGS"}
    ]

    # Eliminar si ya existen para reemplazarlas de manera limpia
    df_cta = df_cta[~df_cta["CuentaID"].isin([a["CuentaID"] for a in industrial_accounts])]
    df_ind = pd.DataFrame(industrial_accounts)
    df_cta = pd.concat([df_cta, df_ind], ignore_index=True)

    df_cta.to_csv(p, index=False, encoding="utf-8")
    print(f"dim_cuentas_contables.csv actualizado con {len(df_cta)} cuentas.")

    # Tambien sincronizar raw_plan_cuentas_contables.csv para mantener coherencia ETL
    p_raw = os.path.join(RAW_DIR, "raw_plan_cuentas_contables.csv")
    if os.path.exists(p_raw):
        df_raw = pd.read_csv(p_raw, encoding="utf-8")
        df_raw = df_raw[~df_raw["CuentaID"].str.strip().isin([a["CuentaID"] for a in industrial_accounts])]
        df_raw = pd.concat([df_raw, df_ind], ignore_index=True)
        df_raw.to_csv(p_raw, index=False, encoding="utf-8")
        print(f"raw_plan_cuentas_contables.csv sincronizado.")
    return df_cta

def update_fact_opex_mensual():
    print("\n--- Actualizando fact_opex_mensual.csv con cuentas industriales ---")
    p = os.path.join(GOLD_DIR, "fact_opex_mensual.csv")
    df_opx = pd.read_csv(p, encoding="utf-8")

    orig_total_pres = df_opx["OPEXPresupuestado"].sum()
    orig_total_real = df_opx["OPEXReal"].sum()

    # Separar registros no fabriles (CC-104, CC-201, CC-202, CC-203)
    df_non_plant = df_opx[~df_opx["CentroCostoID"].isin(["CC-101", "CC-102", "CC-103"])].copy()

    # Tomar la agrupacion original por (DateKey, AnioMes, CentroCostoID) para CC-101, CC-102, CC-103
    df_plant_orig = df_opx[df_opx["CentroCostoID"].isin(["CC-101", "CC-102", "CC-103"])].groupby(
        ["DateKey", "AnioMes", "CentroCostoID"], as_index=False
    ).agg({
        "OPEXPresupuestado": "sum",
        "OPEXReal": "sum"
    })

    plant_rows = []

    for _, row in df_plant_orig.iterrows():
        dk = int(row["DateKey"])
        am = str(row["AnioMes"])
        cc = str(row["CentroCostoID"])
        tot_pres = float(row["OPEXPresupuestado"])
        tot_real = float(row["OPEXReal"])
        m_num = int(am.split("-")[1])

        # Distribucion porcentual segun centro de costo y estacionalidad de vendimia
        if cc == "CC-101": # Elaboracion y Molienda
            # En vendimia (feb, mar, abr, may) gran parte es uva & mosto
            if m_num in [2, 3, 4, 5]:
                dist = [
                    ("CTA-201", 0.65), # Materia Prima Uva & Mosto
                    ("CTA-203", 0.20), # Mano de Obra Directa
                    ("CTA-204", 0.15)  # CIF (Refrigeracion molienda, energia)
                ]
            else:
                dist = [
                    ("CTA-201", 0.42), # Trasiegos, insumos enologicos
                    ("CTA-203", 0.35), # Enologia de bodega
                    ("CTA-204", 0.23)  # CIF (Frío guarda, gas, mantenimiento)
                ]
        elif cc == "CC-102": # Fraccionamiento y Embalaje
            # Insumos secos dominante, mano de obra linea, CIF maquina embotelladora
            dist = [
                ("CTA-202", 0.60), # Insumos Secos
                ("CTA-203", 0.25), # Mano de Obra Fraccionamiento
                ("CTA-204", 0.15)  # CIF Envasado
            ]
        elif cc == "CC-103": # Mantenimiento y Servicios
            # CIF mantenimiento, repuestos, servicios publicos + mano de obra tecnica
            dist = [
                ("CTA-204", 0.70), # CIF (Mantenimiento, gas, energia fabril)
                ("CTA-203", 0.30)  # Mano de Obra de Mantenimiento
            ]

        # Asignar montos garantizando cuadratura exacta al centavo
        allocated_pres = 0.0
        allocated_real = 0.0
        
        for idx, (cta, weight) in enumerate(dist):
            is_last = (idx == len(dist) - 1)
            if not is_last:
                p_amount = round(tot_pres * weight, 2)
                r_amount = round(tot_real * weight, 2)
                allocated_pres += p_amount
                allocated_real += r_amount
            else:
                # Ajuste residual de redondeo exacto
                p_amount = round(tot_pres - allocated_pres, 2)
                r_amount = round(tot_real - allocated_real, 2)

            desvio = round(r_amount - p_amount, 2)
            desvio_pct = round(desvio / p_amount, 4) if p_amount > 0 else 0.0

            plant_rows.append({
                "DateKey": dk,
                "AnioMes": am,
                "CentroCostoID": cc,
                "CuentaID": cta,
                "OPEXPresupuestado": p_amount,
                "OPEXReal": r_amount,
                "DesvioOPEX": desvio,
                "DesvioPorcentual": desvio_pct
            })

    df_plant_new = pd.DataFrame(plant_rows)

    # Combinar y ordenar
    df_final_opx = pd.concat([df_plant_new, df_non_plant], ignore_index=True)
    df_final_opx = df_final_opx.sort_values(by=["DateKey", "CentroCostoID", "CuentaID"]).reset_index(drop=True)

    # Validacion matematica de cuadratura
    new_total_pres = df_final_opx["OPEXPresupuestado"].sum()
    new_total_real = df_final_opx["OPEXReal"].sum()
    diff_pres = abs(new_total_pres - orig_total_pres)
    diff_real = abs(new_total_real - orig_total_real)

    print(f"Total Presupuesto Anterior: {orig_total_pres:,.2f} | Nuevo: {new_total_pres:,.2f} | Dif: {diff_pres:.4f}")
    print(f"Total Real Anterior:        {orig_total_real:,.2f} | Nuevo: {new_total_real:,.2f} | Dif: {diff_real:.4f}")
    assert diff_pres < 0.01, "Error: Descuadre en presupuesto OPEX"
    assert diff_real < 0.01, "Error: Descuadre en real OPEX"

    df_final_opx.to_csv(p, index=False, encoding="utf-8")
    print(f"fact_opex_mensual.csv guardado con {len(df_final_opx)} registros (cuadratura exacta comprobada).")
    return df_final_opx

if __name__ == "__main__":
    update_fact_operaciones_planta()
    create_fact_inventario_guarda()
    update_dim_cuentas_contables()
    update_fact_opex_mensual()
    print("\nTODAS LAS OPERACIONES DE CAPA DE DATOS FINALIZADAS CON EXITO.")
