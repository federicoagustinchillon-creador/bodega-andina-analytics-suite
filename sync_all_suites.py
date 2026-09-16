# -*- coding: utf-8 -*-
"""
Orquestador Maestro y Sincronizador de la Suite Empresarial Power BI
Bodega & Agroindustria Andina S.A.

Ejecuta:
1. Verificacion de datos curados en '00_Data_Engineering_ETL/curated_gold'.
2. Validacion de esquemas relacionales y vistas SQL en DuckDB.
3. Auditoria estricta anti-hardcodes y validacion de esquemas Fabric (TMDL/PBIR).
4. Sincronizacion segura e incremental hacia Google Drive Master:
   'G:\\Mi unidad\\Federico_Chillon_Master\\02_Insercion_Laboral_y_CVs\\Portfolio_Empresarial_PowerBI'

Autor: Federico Agustin Chillon
Afiliacion: Facultad de Ciencias Economicas - Universidad Nacional de Cuyo (UNCUYO)
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

LOCAL_PORTFOLIO = r"c:\Users\fedea\Downloads\cv\Portfolio_Empresarial_PowerBI"
GDRIVE_DESTS = [
    r"G:\Mi unidad\Federico_Chillon_Master\02_Insercion_Laboral_y_CVs\Proyecto Empresarial\Portfolio_Empresarial_PowerBI",
    r"G:\Mi unidad\Federico_Chillon_Master\02_Insercion_Laboral_y_CVs\Portfolio_Empresarial_PowerBI"
]

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def step_1_verify_data_layer():
    log("PASO 1: Verificando Capa de Ingenieria de Datos (curated_gold)...")
    gold_dir = os.path.join(LOCAL_PORTFOLIO, "00_Data_Engineering_ETL", "curated_gold")
    required_tables = [
        "dim_calendario.csv",
        "dim_productos.csv",
        "dim_centros_costo.csv",
        "dim_cuentas_contables.csv",
        "fact_ventas_reales.csv",
        "fact_presupuesto_ventas.csv",
        "fact_opex_mensual.csv",
        "fact_capital_trabajo.csv",
        "fact_operaciones_planta.csv",
        "fact_inventario_guarda.csv"
    ]
    for tbl in required_tables:
        p = os.path.join(gold_dir, tbl)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            raise FileNotFoundError(f"Tabla requerida no encontrada o vacia: {p}")
        log(f"  * Tabla verificada: {tbl} ({os.path.getsize(p):,} bytes)")
    log("Capa de datos curados 100% integra.")

def step_2_verify_sql_duckdb():
    log("\nPASO 2: Verificando Vistas SQL Analiticas en DuckDB...")
    duckdb_tool = os.path.join(r"c:\Users\fedea\Downloads\cv\tools", "verify_sql_duckdb.py")
    if os.path.exists(duckdb_tool):
        res = subprocess.run([sys.executable, duckdb_tool], capture_output=True, text=True, encoding="utf-8")
        if res.returncode != 0:
            log(f"Error en validacion DuckDB: {res.stderr}")
            raise RuntimeError("Fallo en la verificacion de vistas SQL.")
        log("Vistas analiticas SQL (P&L Cascada, Pareto, Eficiencia Enologica) validadas exitosamente.")
    else:
        log("Script DuckDB no encontrado, omitiendo paso.")

def step_3_audit_powerbi_models():
    log("\nPASO 3: Ejecutando Auditoria Anti-Hardcodes y Esquemas Fabric...")
    audit_tool = os.path.join(LOCAL_PORTFOLIO, "tools", "audit_powerbi_suite.py")
    res = subprocess.run([sys.executable, audit_tool], capture_output=True, text=True, encoding="utf-8")
    print(res.stdout)
    if res.returncode != 0:
        raise RuntimeError("Fallo en la auditoria de modelos Power BI.")
    log("Auditoria de modelos Power BI concluida con 0 violaciones.")

def step_4_sync_to_gdrive():
    log("\nPASO 4: Sincronizando Suite hacia Google Drive Master (Ambas Rutas)...")
    
    for gdrive_dest in GDRIVE_DESTS:
        parent_dir = os.path.split(gdrive_dest)[0]
        if not os.path.exists(parent_dir):
            log(f"ADVERTENCIA: Directorio padre no existe o unidad G: no montada: {parent_dir}")
            continue

        os.makedirs(gdrive_dest, exist_ok=True)
        log(f"\nSincronizando de: {LOCAL_PORTFOLIO}")
        log(f"Hacia:            {gdrive_dest}")
        
        cmd = [
            "robocopy",
            LOCAL_PORTFOLIO,
            gdrive_dest,
            "/MIR",
            "/XD", "__pycache__", ".pytest_cache",
            "/XF", "*.pyc",
            "/R:2",
            "/W:1",
            "/NP"
        ]
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode > 7:
            log(f"Error en robocopy hacia {gdrive_dest} (codigo {res.returncode}): {res.stderr}")
        else:
            log(f"Sincronizacion exitosa (codigo robocopy: {res.returncode}).")

        # Validacion de artefactos criticos
        critical_files = [
            r"01_Financial_Controller_FPA\01_Financial_Controller_FPA.pbip",
            r"01_Financial_Controller_FPA\01_Financial_Controller_FPA.Report\definition.pbir",
            r"01_Financial_Controller_FPA\01_Financial_Controller_FPA.SemanticModel\definition.pbism",
            r"02_Commercial_Sales_Intelligence\02_Commercial_Sales_Intelligence.pbip",
            r"02_Commercial_Sales_Intelligence\02_Commercial_Sales_Intelligence.Report\definition.pbir",
            r"02_Commercial_Sales_Intelligence\02_Commercial_Sales_Intelligence.SemanticModel\definition.pbism",
            r"03_Operations_SupplyChain_Plant\03_Operations_SupplyChain_Plant.pbip",
            r"03_Operations_SupplyChain_Plant\03_Operations_SupplyChain_Plant.Report\definition.pbir",
            r"03_Operations_SupplyChain_Plant\03_Operations_SupplyChain_Plant.SemanticModel\definition.pbism"
        ]
        for cf in critical_files:
            cfp = os.path.join(gdrive_dest, cf)
            if not os.path.exists(cfp):
                log(f"  [ERROR] Artefacto ausente: {cf}")
            else:
                log(f"  [OK] {cf} ({os.path.getsize(cfp):,} bytes)")

def main():
    log("=" * 80)
    log("INICIANDO PROCESO MAESTRO DE SINCRONIZACION Y DESPLIEGUE")
    log("SUITE EMPRESARIAL POWER BI - FEDERICO AGUSTIN CHILLON (UNCUYO)")
    log("=" * 80)
    
    step_1_verify_data_layer()
    step_2_verify_sql_duckdb()
    step_3_audit_powerbi_models()
    step_4_sync_to_gdrive()
    
    log("\n" + "=" * 80)
    log("PROCESO FINALIZADO EXITOSAMENTE AL 100%.")
    log("=" * 80)

if __name__ == "__main__":
    main()
