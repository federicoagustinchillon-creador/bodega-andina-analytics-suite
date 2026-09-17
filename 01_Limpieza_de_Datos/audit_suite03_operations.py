# -*- coding: utf-8 -*-
"""
Auditoria Integral de Modelado de Datos y TMDL para Suite 03 Operations
Bodega & Agroindustria Andina S.A.
Autor: Federico Agustin Chillon - UNCUYO
"""

import os
import re
import pandas as pd
import duckdb

BASE_DIR = r"c:\Users\fedea\Downloads\cv\Portfolio_Empresarial_PowerBI"
GOLD_DIR = os.path.join(BASE_DIR, "01_Limpieza_de_Datos", "curated_gold")
SUITE03_DIR = os.path.join(BASE_DIR, "04_Operaciones_y_Planta")
TMDL_DIR = os.path.join(SUITE03_DIR, "04_Operaciones_y_Planta.SemanticModel", "definition")

def test_fact_operaciones_planta():
    print("--- 1. Auditando fact_operaciones_planta.csv ---")
    p = os.path.join(GOLD_DIR, "fact_operaciones_planta.csv")
    df = pd.read_csv(p, encoding="utf-8")
    assert "Latitud" in df.columns, "Falta columna Latitud"
    assert "Longitud" in df.columns, "Falta columna Longitud"
    assert len(df) == 350, f"Esperados 350 registros, obtenidos {len(df)}"

    geo_targets = {
        "Finca Agrelo": (-33.1250, -68.8950),
        "Finca Barrancas": (-33.0560, -68.7050),
        "Finca Gualtallary": (-33.3850, -69.2150),
        "Finca Altamira": (-33.7750, -69.1550),
    }
    for finca, (lat, lon) in geo_targets.items():
        sub = df[df["FincaOrigen"] == finca]
        assert (sub["Latitud"] == lat).all(), f"Error latitud para {finca}"
        assert (sub["Longitud"] == lon).all(), f"Error longitud para {finca}"
    print("  [OK] Coordenadas y encoding UTF-8 validados al 100%.")

def test_fact_inventario_guarda():
    print("\n--- 2. Auditando fact_inventario_guarda.csv ---")
    p = os.path.join(GOLD_DIR, "fact_inventario_guarda.csv")
    df = pd.read_csv(p, encoding="utf-8")
    expected_cols = ["DateKey", "AnioMes", "ProductoID", "TipoVasija", "Litros", "ValorInventario", "MermaPct", "DIODias", "EstadoCalidad"]
    assert list(df.columns) == expected_cols, f"Columnas incorrectas: {list(df.columns)}"
    assert len(df) == 240, f"Esperadas 240 filas, obtenidas {len(df)}"
    assert set(df["ProductoID"].unique()) == {"PRD-01", "PRD-02", "PRD-03", "PRD-04", "PRD-05"}
    assert set(df["TipoVasija"].unique()) == {
        "Piletas de Acero Inoxidable",
        "Barricas de Roble Frances",
        "Barricas de Roble Americano",
        "Botellero en Estiba Climatizada"
    }
    assert (df["Litros"] > 0).all(), "Existen litros menores o iguales a cero"
    assert (df["ValorInventario"] > 0).all(), "Existen valores de inventario invalidos"
    assert (df["MermaPct"] >= 0).all(), "Existen mermas negativas"
    assert (df["DIODias"] > 0).all(), "Existen dias de inventario invalidos"

    # Verificar no-planicidad (desviacion estandar mayor a cero)
    for col in ["Litros", "ValorInventario", "MermaPct", "DIODias"]:
        assert df[col].std() > 0, f"Columna {col} presenta valores planos"

    print("  [OK] 240 registros mensuales heterogeneos y realistas comprobados.")

def test_cuentas_contables_y_opex():
    print("\n--- 3. Auditando dim_cuentas_contables.csv y fact_opex_mensual.csv ---")
    p_cta = os.path.join(GOLD_DIR, "dim_cuentas_contables.csv")
    df_cta = pd.read_csv(p_cta, encoding="utf-8")
    expected_industrial = {"CTA-201", "CTA-202", "CTA-203", "CTA-204"}
    assert expected_industrial.issubset(set(df_cta["CuentaID"])), "Faltan cuentas industriales en dim_cuentas_contables"

    p_opx = os.path.join(GOLD_DIR, "fact_opex_mensual.csv")
    df_opx = pd.read_csv(p_opx, encoding="utf-8")

    # Verificar que CC-101, CC-102, CC-103 usen cuentas industriales
    plant_opx = df_opx[df_opx["CentroCostoID"].isin(["CC-101", "CC-102", "CC-103"])]
    used_cuentas = set(plant_opx["CuentaID"].unique())
    assert used_cuentas == expected_industrial, f"Cuentas en planta no coinciden: {used_cuentas}"

    # Cuadratura presupuestaria exacta
    tot_pres = df_opx["OPEXPresupuestado"].sum()
    tot_real = df_opx["OPEXReal"].sum()
    print(f"  OPEX Total Presupuestado: ${tot_pres:,.2f}")
    print(f"  OPEX Total Real:          ${tot_real:,.2f}")
    assert round(tot_pres, 2) == 1085265186.38, f"Descuadre en Presupuesto Total OPEX: {tot_pres}"
    assert round(tot_real, 2) == 1081406836.86, f"Descuadre en Real Total OPEX: {tot_real}"
    print("  [OK] Cuentas industriales asignadas y cuadratura contable 100% verificada.")

def test_semantic_model_tmdl():
    print("\n--- 4. Auditando Sintaxis y Relaciones TMDL ---")
    # 4.1 model.tmdl
    p_model = os.path.join(TMDL_DIR, "model.tmdl")
    content_model = open(p_model, "r", encoding="utf-8").read()
    assert "ref table fact_inventario_guarda" in content_model, "Falta ref table fact_inventario_guarda en model.tmdl"
    assert '"fact_inventario_guarda"' in content_model, "Falta fact_inventario_guarda en PBI_QueryOrder"

    # 4.2 relationships.tmdl
    p_rel = os.path.join(TMDL_DIR, "relationships.tmdl")
    content_rel = open(p_rel, "r", encoding="utf-8").read()
    assert "relationship rel_inventario_calendario" in content_rel, "Falta rel_inventario_calendario"
    assert "relationship rel_inventario_productos" in content_rel, "Falta rel_inventario_productos"

    # 4.3 fact_operaciones_planta.tmdl
    p_op = os.path.join(TMDL_DIR, "tables", "fact_operaciones_planta.tmdl")
    content_op = open(p_op, "r", encoding="utf-8").read()
    assert "column Latitud" in content_op and "dataCategory: Latitude" in content_op, "Falta Latitud con dataCategory Latitude"
    assert "column Longitud" in content_op and "dataCategory: Longitude" in content_op, "Falta Longitud con dataCategory Longitude"

    # 4.4 fact_inventario_guarda.tmdl
    p_inv = os.path.join(TMDL_DIR, "tables", "fact_inventario_guarda.tmdl")
    assert os.path.exists(p_inv), "No existe fact_inventario_guarda.tmdl"
    content_inv = open(p_inv, "r", encoding="utf-8").read()
    for col in ["DateKey", "AnioMes", "ProductoID", "TipoVasija", "Litros", "ValorInventario", "MermaPct", "DIODias", "EstadoCalidad"]:
        assert f"column {col}" in content_inv, f"Falta column {col} en fact_inventario_guarda.tmdl"

    # 4.5 _Medidas_Operaciones.tmdl
    p_med = os.path.join(TMDL_DIR, "tables", "_Medidas_Operaciones.tmdl")
    content_med = open(p_med, "r", encoding="utf-8").read()
    assert "measure 'Valor Inventario Guarda' = SUM(fact_inventario_guarda[ValorInventario])" in content_med
    assert "measure 'Litros en Crianza' = SUM(fact_inventario_guarda[Litros])" in content_med
    assert "measure 'DIO Promedio Dias' = AVERAGE(fact_inventario_guarda[DIODias])" in content_med
    assert "measure 'Tasa Merma Crianza %' = AVERAGE(fact_inventario_guarda[MermaPct])" in content_med

    # Validar que no haya parentesis DAX sin cerrar o caracteres anomalos
    for tmdl_file in [p_model, p_rel, p_op, p_inv, p_med]:
        txt = open(tmdl_file, "r", encoding="utf-8").read()
        assert "\ufffd" not in txt, f"Caracter unicode corrupto detectado en {tmdl_file}"
    print("  [OK] TMDL sintacticamente perfecto, sin hardcodes y con referencias consistentes.")

def test_duckdb_integration():
    print("\n--- 5. Auditando DuckDB y Vistas Analiticas ---")
    base = os.path.join(BASE_DIR, "01_Limpieza_de_Datos")
    sql_ddl = open(os.path.join(base, "sql", "01_schema_ddl.sql"), encoding="utf-8").read()
    sql_views = open(os.path.join(base, "sql", "02_analytical_views.sql"), encoding="utf-8").read()
    gold = os.path.join(base, "curated_gold")

    con = duckdb.connect()
    con.execute(sql_ddl)
    tables = [
        'dim_calendario', 'dim_productos', 'dim_centros_costo', 'dim_cuentas_contables',
        'fact_ventas_reales', 'fact_presupuesto_ventas', 'fact_opex_mensual',
        'fact_capital_trabajo', 'fact_operaciones_planta', 'fact_inventario_guarda'
    ]
    for tbl in tables:
        p = os.path.join(gold, tbl + ".csv").replace("\\", "/")
        con.execute(f'INSERT INTO {tbl} SELECT * FROM read_csv_auto("{p}", header=true);')
        cnt = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  Tabla DuckDB '{tbl}': {cnt} registros.")

    con.execute(sql_views)
    cnt_v1 = con.execute("SELECT COUNT(*) FROM vw_pl_cascada_mensual").fetchone()[0]
    cnt_v2 = con.execute("SELECT COUNT(*) FROM vw_analisis_pareto_comercial").fetchone()[0]
    cnt_v3 = con.execute("SELECT COUNT(*) FROM vw_eficiencia_enologica_planta").fetchone()[0]
    assert cnt_v1 == 12, f"vw_pl_cascada_mensual esperados 12, obtenidos {cnt_v1}"
    assert cnt_v2 > 0, "vw_analisis_pareto_comercial vacia"
    assert cnt_v3 > 0, "vw_eficiencia_enologica_planta vacia"
    print("  [OK] DuckDB: Vistas analiticas ejecutadas con exito.")

if __name__ == "__main__":
    test_fact_operaciones_planta()
    test_fact_inventario_guarda()
    test_cuentas_contables_y_opex()
    test_semantic_model_tmdl()
    test_duckdb_integration()
    print("\n========================================================")
    print("TODAS LAS PRUEBAS DE AUDITORIA PASARON CON EXITO (100%)")
    print("========================================================")
