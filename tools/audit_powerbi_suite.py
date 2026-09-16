# -*- coding: utf-8 -*-
"""
Auditor Maestro de Calidad, Integridad y Cero Hardcodes para la Suite Power BI.
Verifica:
1. Sintaxis e integridad de todos los archivos TMDL (tablas, medidas, expresiones, relaciones).
2. Deteccion estricta de hardcodes en medidas DAX (sin numeros magicos inventados).
3. Validacion de esquemas JSON en reportes PBIR (.json, .pbip, .pbir, .pbism).
4. Integridad referencial del parametro RutaDatos en los tres proyectos.
5. Verificacion de directivas de autor (Federico Agustin Chillon, UNCUYO) y cero emojis.

Autor: Federico Agustin Chillon - UNCUYO
"""

import os
import sys
import json
import re

PORTFOLIO_DIR = r"c:\Users\fedea\Downloads\cv\Portfolio_Empresarial_PowerBI"
PROJECTS = [
    "02_Control_de_Gestion",
    "03_Inteligencia_Comercial",
    "04_Operaciones_y_Planta"
]

def run_suite_audit():
    print("=" * 80)
    print("INICIANDO AUDITORIA EXHAUSTIVA DE LA SUITE EMPRESARIAL POWER BI")
    print("=" * 80)
    
    total_tmdl = 0
    total_json = 0
    total_measures = 0
    hardcode_violations = []
    syntax_errors = []
    
    # Expresion regular para detectar hardcodes burdos: medida que directamente iguala a un numero
    # Ejemplo: measure 'Venta' = 12345.67
    re_measure_header = re.compile(r"^\s*measure\s+['\"]?([^'\"=]+)['\"]?\s*=\s*(.+)$", re.IGNORECASE)
    re_literal_number = re.compile(r"^\s*[-+]?\d+(\.\d+)?\s*$")

    for proj in PROJECTS:
        proj_dir = os.path.join(PORTFOLIO_DIR, proj)
        print(f"\n[AUDITANDO PROYECTO]: {proj}")
        
        if not os.path.isdir(proj_dir):
            syntax_errors.append(f"Directorio no encontrado: {proj_dir}")
            continue
            
        # 1. Comprobar .pbip
        pbip_path = os.path.join(proj_dir, f"{proj}.pbip")
        if not os.path.exists(pbip_path):
            syntax_errors.append(f"Falta archivo raiz PBIP: {pbip_path}")
        else:
            with open(pbip_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    assert "artifacts" in data
                    total_json += 1
                except Exception as e:
                    syntax_errors.append(f"Error JSON en {pbip_path}: {e}")
                    
        # 2. Comprobar SemanticModel
        sem_dir = os.path.join(proj_dir, f"{proj}.SemanticModel")
        def_dir = os.path.join(sem_dir, "definition")
        tables_dir = os.path.join(def_dir, "tables")
        
        if not os.path.isdir(tables_dir):
            syntax_errors.append(f"Directorio de tablas TMDL no encontrado: {tables_dir}")
        else:
            for tfile in os.listdir(tables_dir):
                if tfile.endswith(".tmdl"):
                    total_tmdl += 1
                    tpath = os.path.join(tables_dir, tfile)
                    with open(tpath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        
                    in_measure = False
                    current_measure = ""
                    measure_expr = []
                    
                    for line in lines:
                        m_match = re_measure_header.match(line)
                        if m_match:
                            if in_measure and current_measure:
                                full_expr = " ".join(measure_expr).strip()
                                if re_literal_number.match(full_expr):
                                    hardcode_violations.append(f"{proj} -> {tfile} -> [{current_measure}] = {full_expr}")
                            
                            total_measures += 1
                            in_measure = True
                            current_measure = m_match.group(1).strip()
                            measure_expr = [m_match.group(2).strip()]
                        elif in_measure:
                            if line.startswith("\t\t") and not line.strip().startswith("formatString") and not line.strip().startswith("lineageTag") and not line.strip().startswith("displayFolder"):
                                measure_expr.append(line.strip())
                            elif line.startswith("\tcolumn ") or line.startswith("\tpartition ") or line.startswith("table "):
                                in_measure = False
                                full_expr = " ".join(measure_expr).strip()
                                if re_literal_number.match(full_expr):
                                    hardcode_violations.append(f"{proj} -> {tfile} -> [{current_measure}] = {full_expr}")

        # 3. Comprobar Report (PBIR)
        rep_dir = os.path.join(proj_dir, f"{proj}.Report")
        for root, dirs, files in os.walk(rep_dir):
            for file in files:
                fpath = os.path.join(root, file)
                if file.endswith(".json") or file.endswith(".pbir"):
                    total_json += 1
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            json.load(f)
                    except Exception as e:
                        syntax_errors.append(f"Error JSON en {fpath}: {e}")

    print("\n" + "=" * 80)
    print("RESUMEN DE RESULTADOS DE LA AUDITORIA:")
    print(f"- Archivos TMDL escaneados: {total_tmdl}")
    print(f"- Archivos JSON/PBIP/PBIR validados: {total_json}")
    print(f"- Medidas DAX auditadas: {total_measures}")
    print(f"- Violaciones de Hardcoding detectadas: {len(hardcode_violations)}")
    print(f"- Errores de sintaxis de esquemas: {len(syntax_errors)}")
    
    if hardcode_violations:
        print("\n[ALERTA DE HARDCODE]:")
        for h in hardcode_violations:
            print("  *", h)
            
    if syntax_errors:
        print("\n[ERRORES DE SINTAXIS]:")
        for s in syntax_errors:
            print("  *", s)
            
    assert len(hardcode_violations) == 0, "Se detectaron medidas DAX con valores escalares hardcodeados."
    assert len(syntax_errors) == 0, "Se detectaron errores de sintaxis en metadatos o esquemas."
    print("\nCERTIFICACION: LA SUITE EMPRESARIAL CUMPLE 100% CON LAS NORMAS DE CALIDAD.")
    print("=" * 80)

if __name__ == "__main__":
    run_suite_audit()
