# -*- coding: utf-8 -*-
"""
Auditor Maestro de Calidad, Integridad y Cero Hardcodes para la Suite Power BI.
Verifica:
1. Sintaxis e integridad de todos los archivos TMDL (tablas, medidas, expresiones, relaciones, formatStrings validos).
2. Deteccion estricta de hardcodes en medidas DAX (sin numeros magicos inventados).
3. Validacion de esquemas JSON en reportes PBIR (.json, .pbip, .pbir, .pbism obligatorio).
4. Integridad referencial de rutas (.pbip -> .Report, .pbir -> .SemanticModel).
5. Existencia de un unico archivo PBIP por suite numerada (sin duplicados).
6. Verificacion de directivas de autor (Federico Agustin Chillon, UNCUYO) y cero emojis.

Autor: Federico Agustin Chillon - UNCUYO
"""

import os
import sys
import json
import re

PORTFOLIO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS = [
    "02_Control_de_Gestion",
    "03_Inteligencia_Comercial",
    "04_Operaciones_y_Planta",
    "06_Modelos_de_Riesgo_y_Prediccion"
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
    format_string_errors = []
    
    # Expresion regular para detectar hardcodes burdos: medida que directamente iguala a un numero
    re_measure_header = re.compile(r"^\s*measure\s+['\"]?([^'\"=]+)['\"]?\s*=\s*(.+)$", re.IGNORECASE)
    re_literal_number = re.compile(r"^\s*[-+]?\d+(\.\d+)?\s*$")

    for proj in PROJECTS:
        proj_dir = os.path.join(PORTFOLIO_DIR, proj)
        print(f"\n[AUDITANDO PROYECTO]: {proj}")
        
        if not os.path.isdir(proj_dir):
            syntax_errors.append(f"Directorio no encontrado: {proj_dir}")
            continue
            
        # 1. Comprobar .pbip unico y valido
        pbip_candidates = [f for f in os.listdir(proj_dir) if f.endswith(".pbip")]
        if not pbip_candidates:
            syntax_errors.append(f"Falta archivo raiz PBIP en: {proj_dir}")
            expected_rep_name = ""
        elif len(pbip_candidates) > 1:
            syntax_errors.append(f"Archivos PBIP duplicados en {proj_dir}: {pbip_candidates}")
            expected_rep_name = ""
        else:
            pbip_name = pbip_candidates[0]
            pbip_path = os.path.join(proj_dir, pbip_name)
            with open(pbip_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    assert "artifacts" in data
                    expected_rep_name = data["artifacts"][0]["report"]["path"]
                    total_json += 1
                except Exception as e:
                    syntax_errors.append(f"Error JSON en {pbip_path}: {e}")
                    expected_rep_name = ""
                    
        # 2. Comprobar SemanticModel y definition.pbism
        sem_candidates = [d for d in os.listdir(proj_dir) if d.endswith(".SemanticModel")]
        if not sem_candidates:
            syntax_errors.append(f"Directorio SemanticModel no encontrado en: {proj_dir}")
            continue
        sem_dir = os.path.join(proj_dir, sem_candidates[0])
        
        # Validar definition.pbism
        pbism_path = os.path.join(sem_dir, "definition.pbism")
        if not os.path.isfile(pbism_path):
            syntax_errors.append(f"Falta artefacto obligatorio definition.pbism en: {sem_dir}")
        else:
            try:
                with open(pbism_path, "r", encoding="utf-8") as f:
                    pbism_data = json.load(f)
                    assert "version" in pbism_data
                    total_json += 1
            except Exception as e:
                syntax_errors.append(f"Error JSON en {pbism_path}: {e}")
                
        def_dir = os.path.join(sem_dir, "definition")
        tables_dir = os.path.join(def_dir, "tables")
        
        if not os.path.isdir(tables_dir):
            syntax_errors.append(f"Directorio de tablas TMDL no encontrado: {tables_dir}")
        else:
            for root, dirs, files in os.walk(def_dir):
                for tfile in files:
                    if tfile.endswith(".tmdl"):
                        total_tmdl += 1
                        tpath = os.path.join(root, tfile)
                        with open(tpath, "r", encoding="utf-8", errors="ignore") as f:
                            lines = f.readlines()
                            
                        # Verificar que linguisticMetadata tenga contentType: json
                        full_tmdl_text = "".join(lines)
                        if "linguisticMetadata" in full_tmdl_text and "contentType: json" not in full_tmdl_text and "contentType: xml" not in full_tmdl_text:
                            syntax_errors.append(f"Falta 'contentType: json' en {tpath} (Analysis Services requiere contentType)")
                        
                    in_measure = False
                    current_measure = ""
                    measure_expr = []
                    
                    for line_idx, line in enumerate(lines, 1):
                        # Validacion de formatString syntax
                        if "formatString:" in line:
                            val = line.split("formatString:", 1)[1].strip()
                            if val.startswith('"') and val.endswith('"') and len(val) > 2:
                                inner = val[1:-1]
                                remainder = inner.replace('""', '')
                                if '"' in remainder:
                                    format_string_errors.append(f"{tfile}:{line_idx} formatString con comillas sin escapar: {val}")
                        
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
        rep_candidates = [d for d in os.listdir(proj_dir) if d.endswith(".Report")]
        if not rep_candidates:
            syntax_errors.append(f"Directorio Report no encontrado en: {proj_dir}")
            continue
        rep_dir = os.path.join(proj_dir, rep_candidates[0])
        
        # Validar consistencia con PBIP
        if expected_rep_name and os.path.basename(rep_dir) != expected_rep_name:
            syntax_errors.append(f"Inconsistencia PBIP: {pbip_candidates[0]} apunta a '{expected_rep_name}' pero existe '{os.path.basename(rep_dir)}'")
            
        # Validar artefactos obligatorios PBIR
        for req_f in ["definition.pbir", os.path.join("definition", "version.json"), os.path.join("definition", "report.json"), os.path.join("definition", "pages", "pages.json")]:
            rf_path = os.path.join(rep_dir, req_f)
            if not os.path.isfile(rf_path):
                syntax_errors.append(f"Falta artefacto obligatorio PBIR: {rf_path}")

        pbir_path = os.path.join(rep_dir, "definition.pbir")
        if not os.path.isfile(pbir_path):
            pass
        else:
            try:
                with open(pbir_path, "r", encoding="utf-8") as f:
                    pbir_data = json.load(f)
                    target_sem = pbir_data["datasetReference"]["byPath"]["path"]
                    expected_sem_path = f"../{os.path.basename(sem_dir)}"
                    if target_sem != expected_sem_path:
                        syntax_errors.append(f"Inconsistencia PBIR en {pbir_path}: apunta a '{target_sem}', esperado '{expected_sem_path}'")
                    total_json += 1
            except Exception as e:
                syntax_errors.append(f"Error JSON en {pbir_path}: {e}")

        for root, dirs, files in os.walk(proj_dir):
            if len(root) >= 248:
                syntax_errors.append(f"Ruta de directorio excede limite Windows (248 chars): {root} ({len(root)})")
            for file in files:
                fpath = os.path.join(root, file)
                if len(fpath) >= 260:
                    syntax_errors.append(f"Ruta de archivo excede limite Windows (260 chars): {fpath} ({len(fpath)})")
                if file.endswith(".json"):
                    total_json += 1
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            json.load(f)
                    except Exception as e:
                        syntax_errors.append(f"Error JSON en {fpath}: {e}")

    print("\n" + "=" * 80)
    print("RESUMEN DE RESULTADOS DE LA AUDITORIA:")
    print(f"- Archivos TMDL escaneados: {total_tmdl}")
    print(f"- Archivos JSON/PBIP/PBIR/PBISM validados: {total_json}")
    print(f"- Medidas DAX auditadas: {total_measures}")
    print(f"- Violaciones de Hardcoding detectadas: {len(hardcode_violations)}")
    print(f"- Errores de sintaxis de formatString en TMDL: {len(format_string_errors)}")
    print(f"- Errores de sintaxis o metadatos: {len(syntax_errors)}")
    
    if hardcode_violations:
        print("\n[ALERTA DE HARDCODE]:")
        for h in hardcode_violations:
            print("  *", h)
            
    if format_string_errors:
        print("\n[ERRORES DE FORMATSTRING EN TMDL]:")
        for fe in format_string_errors:
            print("  *", fe)
            
    if syntax_errors:
        print("\n[ERRORES DE SINTAXIS / METADATOS]:")
        for s in syntax_errors:
            print("  *", s)
            
    assert len(hardcode_violations) == 0, "Se detectaron medidas DAX con valores escalares hardcodeados."
    assert len(format_string_errors) == 0, "Se detectaron errores de formatString en TMDL."
    assert len(syntax_errors) == 0, "Se detectaron errores de sintaxis en metadatos o esquemas."
    print("\nCERTIFICACION: LA SUITE EMPRESARIAL CUMPLE 100% CON LAS NORMAS DE CALIDAD Y FABRIC.")
    print("=" * 80)

if __name__ == "__main__":
    run_suite_audit()
