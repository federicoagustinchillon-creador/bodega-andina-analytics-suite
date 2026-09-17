# -*- coding: utf-8 -*-
"""
Actualizador Maestro de Matrices Analiticas con Semaforos y Reglas de Decision Prescriptivas.
Inyecta en cada matriz original de la suite:
1. 04_Operaciones_y_Planta:
   - p1_vendimia / v_tbl_rem: Semaforo Rendimiento Extraccion & Prescripcion Rendimiento Enologico.
   - p2_costos / v_tbl_cst: Tasa Desvio Absorcion %, Semaforo Absorcion Fabril & Regla Decision Absorcion Fabril.
   - p3_mermas / v_tbl_stk: Semaforo Merma Crianza & Prescripcion Guarda y Crianza.
2. 03_Inteligencia_Comercial:
   - p3_pareto / v_tbl_abc: Recomendacion Estrategica ABC.
   - p2_precio / v_tbl_prc: Semaforo Variacion Precio & Regla Decision Precio.
3. 02_Control_de_Gestion:
   - p2_ceco / v_tbl1: Alerta Semaforo OPEX.
   - p4_tesoreria / v_tbl_cobranzas: Recomendacion Cobertura.
4. 06_Modelos_de_Riesgo_y_Prediccion:
   - p3_stress_testing_var / v_tbl_stress: Semaforo Basilea.

Autor: Federico Agustin Chillon - UNCUYO
"""

import os
import json
import uuid

PORTFOLIO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def update_04_operaciones_matrices():
    print("\n--- Actualizando Matrices en 04_Operaciones_y_Planta ---")
    pages_dir = os.path.join(PORTFOLIO_DIR, "04_Operaciones_y_Planta", "Operaciones_y_Planta.Report", "definition", "pages")
    
    # 1. p2_costos / v_tbl_cst
    cst_path = os.path.join(pages_dir, "p2_costos", "visuals", "v_tbl_cst", "visual.json")
    with open(cst_path, "r", encoding="utf-8") as f:
        d = json.load(f)
        
    projs = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "CentrosCosto"}}, "Property": "CentroCostoID"}},
            "queryRef": "CentrosCosto.CentroCostoID",
            "nativeQueryRef": "CentroCostoID",
            "displayName": "CeCo"
        },
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "CentrosCosto"}}, "Property": "NombreCentroCosto"}},
            "queryRef": "CentrosCosto.NombreCentroCosto",
            "nativeQueryRef": "NombreCentroCosto",
            "displayName": "Centro Costo"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Costo Fabril Real Centro"}},
            "queryRef": "_Medidas_Operaciones.Costo Fabril Real Centro",
            "nativeQueryRef": "Costo Fabril Real Centro",
            "displayName": "Real ($)"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Costo Fabril Plan Centro"}},
            "queryRef": "_Medidas_Operaciones.Costo Fabril Plan Centro",
            "nativeQueryRef": "Costo Fabril Plan Centro",
            "displayName": "Plan ($)"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Desvio Fabril Centro"}},
            "queryRef": "_Medidas_Operaciones.Desvio Fabril Centro",
            "nativeQueryRef": "Desvio Fabril Centro",
            "displayName": "Desvío ($)"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Tasa Desvio Absorcion %"}},
            "queryRef": "_Medidas_Operaciones.Tasa Desvio Absorcion %",
            "nativeQueryRef": "Tasa Desvio Absorcion %",
            "displayName": "Tasa Absorción %"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Semaforo Absorcion Fabril"}},
            "queryRef": "_Medidas_Operaciones.Semaforo Absorcion Fabril",
            "nativeQueryRef": "Semaforo Absorcion Fabril",
            "displayName": "Semáforo Absorción"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Regla Decision Absorcion Fabril"}},
            "queryRef": "_Medidas_Operaciones.Regla Decision Absorcion Fabril",
            "nativeQueryRef": "Regla Decision Absorcion Fabril",
            "displayName": "Regla de Decisión Fabril"
        }
    ]
    d["visual"]["query"]["queryState"]["Values"]["projections"] = projs
    # Actualizar dimensiones geometricas para dar espacio al semaforo y regla
    d["position"]["x"] = 196.27
    d["position"]["y"] = 499.2
    d["position"]["width"] = 620
    d["position"]["height"] = 209.07
    
    # Actualizar filtros
    filters = []
    for p in projs:
        fname = uuid.uuid4().hex[:20]
        f_type = "Categorical" if "Column" in p["field"] else "Advanced"
        filters.append({"name": fname, "field": p["field"], "type": f_type})
    d["filterConfig"] = {"filters": filters}
    
    with open(cst_path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print("  + p2_costos / v_tbl_cst actualizado con 8 columnas de absorcion y semaforo.")
    
    # Ajustar visual companero v_bar_desv_cst
    bar_path = os.path.join(pages_dir, "p2_costos", "visuals", "v_bar_desv_cst", "visual.json")
    if os.path.exists(bar_path):
        with open(bar_path, "r", encoding="utf-8") as f:
            bd = json.load(f)
        bd["position"]["x"] = 830
        bd["position"]["y"] = 499.2
        bd["position"]["width"] = 435
        bd["position"]["height"] = 209.07
        with open(bar_path, "w", encoding="utf-8") as f:
            json.dump(bd, f, indent=2, ensure_ascii=False)
        print("  + p2_costos / v_bar_desv_cst reposicionado a x=830, w=435.")

    # 2. p3_mermas / v_tbl_stk
    stk_path = os.path.join(pages_dir, "p3_mermas", "visuals", "v_tbl_stk", "visual.json")
    with open(stk_path, "r", encoding="utf-8") as f:
        d = json.load(f)
        
    projs = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Productos"}}, "Property": "SKU"}},
            "queryRef": "Productos.SKU",
            "nativeQueryRef": "SKU",
            "displayName": "SKU"
        },
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Productos"}}, "Property": "Descripcion"}},
            "queryRef": "Productos.Descripcion",
            "nativeQueryRef": "Descripcion",
            "displayName": "Producto / Etiqueta"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Litros en Crianza"}},
            "queryRef": "_Medidas_Operaciones.Litros en Crianza",
            "nativeQueryRef": "Litros en Crianza",
            "displayName": "Litros Guarda"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Valor Inventario Guarda"}},
            "queryRef": "_Medidas_Operaciones.Valor Inventario Guarda",
            "nativeQueryRef": "Valor Inventario Guarda",
            "displayName": "Valor ($)"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "DIO Promedio Dias"}},
            "queryRef": "_Medidas_Operaciones.DIO Promedio Dias",
            "nativeQueryRef": "DIO Promedio Dias",
            "displayName": "Días (DIO)"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Tasa Merma Crianza %"}},
            "queryRef": "_Medidas_Operaciones.Tasa Merma Crianza %",
            "nativeQueryRef": "Tasa Merma Crianza %",
            "displayName": "Merma (%)"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Semaforo Merma Crianza"}},
            "queryRef": "_Medidas_Operaciones.Semaforo Merma Crianza",
            "nativeQueryRef": "Semaforo Merma Crianza",
            "displayName": "Semáforo Merma"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Prescripcion Guarda y Crianza"}},
            "queryRef": "_Medidas_Operaciones.Prescripcion Guarda y Crianza",
            "nativeQueryRef": "Prescripcion Guarda y Crianza",
            "displayName": "Prescripción Guarda & Crianza"
        }
    ]
    d["visual"]["query"]["queryState"]["Values"]["projections"] = projs
    d["position"]["x"] = 196.27
    d["position"]["y"] = 467.91
    d["position"]["width"] = 660
    d["position"]["height"] = 251.73
    
    filters = []
    for p in projs:
        fname = uuid.uuid4().hex[:20]
        f_type = "Categorical" if "Column" in p["field"] else "Advanced"
        filters.append({"name": fname, "field": p["field"], "type": f_type})
    d["filterConfig"] = {"filters": filters}
    
    with open(stk_path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print("  + p3_mermas / v_tbl_stk actualizado con 8 columnas de mermas y prescripcion.")
    
    # Ajustar visual donut
    dnt_path = os.path.join(pages_dir, "p3_mermas", "visuals", "v_donut_crianza", "visual.json")
    if os.path.exists(dnt_path):
        with open(dnt_path, "r", encoding="utf-8") as f:
            dd = json.load(f)
        dd["position"]["x"] = 870
        dd["position"]["y"] = 413
        dd["position"]["width"] = 395
        dd["position"]["height"] = 295
        with open(dnt_path, "w", encoding="utf-8") as f:
            json.dump(dd, f, indent=2, ensure_ascii=False)
        print("  + p3_mermas / v_donut_crianza reposicionado a x=870, w=395.")

    # 3. p1_vendimia / v_tbl_rem
    rem_path = os.path.join(pages_dir, "p1_vendimia", "visuals", "v_tbl_rem", "visual.json")
    with open(rem_path, "r", encoding="utf-8") as f:
        d = json.load(f)
        
    projs = [
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "ProduccionPlanta"}}, "Property": "FincaOrigen"}},
            "queryRef": "ProduccionPlanta.FincaOrigen",
            "nativeQueryRef": "FincaOrigen",
            "displayName": "Finca"
        },
        {
            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "ProduccionPlanta"}}, "Property": "VariedadUva"}},
            "queryRef": "ProduccionPlanta.VariedadUva",
            "nativeQueryRef": "VariedadUva",
            "displayName": "Varietal"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Total Kilos Uva"}},
            "queryRef": "_Medidas_Operaciones.Total Kilos Uva",
            "nativeQueryRef": "Total Kilos Uva",
            "displayName": "Kilos Uva"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Total Litros Mosto"}},
            "queryRef": "_Medidas_Operaciones.Total Litros Mosto",
            "nativeQueryRef": "Total Litros Mosto",
            "displayName": "Litros Mosto"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Rendimiento Medio Extraccion %"}},
            "queryRef": "_Medidas_Operaciones.Rendimiento Medio Extraccion %",
            "nativeQueryRef": "Rendimiento Medio Extraccion %",
            "displayName": "Rendimiento %"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Semaforo Rendimiento Extraccion"}},
            "queryRef": "_Medidas_Operaciones.Semaforo Rendimiento Extraccion",
            "nativeQueryRef": "Semaforo Rendimiento Extraccion",
            "displayName": "Semáforo Rendimiento"
        },
        {
            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Operaciones"}}, "Property": "Prescripcion Rendimiento Enologico"}},
            "queryRef": "_Medidas_Operaciones.Prescripcion Rendimiento Enologico",
            "nativeQueryRef": "Prescripcion Rendimiento Enologico",
            "displayName": "Prescripción Enológica"
        }
    ]
    d["visual"]["query"]["queryState"]["Values"]["projections"] = projs
    d["position"]["x"] = 196.27
    d["position"]["y"] = 412.44
    d["position"]["width"] = 620
    d["position"]["height"] = 295.82
    
    filters = []
    for p in projs:
        fname = uuid.uuid4().hex[:20]
        f_type = "Categorical" if "Column" in p["field"] else "Advanced"
        filters.append({"name": fname, "field": p["field"], "type": f_type})
    d["filterConfig"] = {"filters": filters}
    
    with open(rem_path, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print("  + p1_vendimia / v_tbl_rem actualizado con 7 columnas de vendimia y prescripcion.")
    
    # Ajustar visual companero v_col_var
    col_path = os.path.join(pages_dir, "p1_vendimia", "visuals", "v_col_var", "visual.json")
    if os.path.exists(col_path):
        with open(col_path, "r", encoding="utf-8") as f:
            cd = json.load(f)
        cd["position"]["x"] = 830
        cd["position"]["y"] = 412.44
        cd["position"]["width"] = 435
        cd["position"]["height"] = 295.82
        with open(col_path, "w", encoding="utf-8") as f:
            json.dump(cd, f, indent=2, ensure_ascii=False)
        print("  + p1_vendimia / v_col_var reposicionado a x=830, w=435.")

def update_03_comercial_matrices():
    print("\n--- Actualizando Matrices en 03_Inteligencia_Comercial ---")
    pages_dir = os.path.join(PORTFOLIO_DIR, "03_Inteligencia_Comercial", "Inteligencia_Comercial.Report", "definition", "pages")
    
    # 1. Inyectar medidas en _Medidas_Comercial.tmdl si faltan
    tmdl_path = os.path.join(PORTFOLIO_DIR, "03_Inteligencia_Comercial", "03_Inteligencia_Comercial.SemanticModel", "definition", "tables", "_Medidas_Comercial.tmdl")
    with open(tmdl_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    if "Semaforo Variacion Precio" not in content:
        new_measures = """
\tmeasure 'Semaforo Variacion Precio' =
\t\t\tSWITCH(
\t\t\t\tTRUE(),
\t\t\t\t[Desvio Precio Promedio] < -300, "DESCUENTO CRITICO",
\t\t\t\t[Desvio Precio Promedio] < 0, "BAJO PRECIO PLAN",
\t\t\t\t"PRECIO ALINEADO"
\t\t\t)
\t\tdisplayFolder: 02_Precios_y_Rentabilidad
\t\tlineageTag: e83017a1-1209-42b1-912a-3819fa019234

\tmeasure 'Regla Decision Precio' =
\t\t\tSWITCH(
\t\t\t\tTRUE(),
\t\t\t\t[Desvio Precio Promedio] < -300, "REGLA: Suspender bonificaciones no autorizadas y renegociar lista con canal mayorista.",
\t\t\t\t[Desvio Precio Promedio] < 0, "REGLA: Revisar cumplimiento de escala de volumen antes de otorgar descuentos.",
\t\t\t\t"ESTRATEGIA: Mantener condiciones contractuales vigentes y defender margen unitario."
\t\t\t)
\t\tdisplayFolder: 02_Precios_y_Rentabilidad
\t\tlineageTag: f94128b2-2310-53c2-823b-4920fa120345
"""
        with open(tmdl_path, "a", encoding="utf-8") as f:
            f.write(new_measures)
        print("  + Medidas 'Semaforo Variacion Precio' y 'Regla Decision Precio' inyectadas en _Medidas_Comercial.tmdl.")

    # 2. p3_pareto / v_tbl_abc
    abc_path = os.path.join(pages_dir, "p3_pareto", "visuals", "v_tbl_abc", "visual.json")
    if os.path.exists(abc_path):
        with open(abc_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        projs = d["visual"]["query"]["queryState"]["Values"]["projections"]
        has_rec = any(p.get("nativeQueryRef") == "Recomendacion Estrategica ABC" for p in projs)
        if not has_rec:
            projs.append({
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Comercial"}}, "Property": "Recomendacion Estrategica ABC"}},
                "queryRef": "_Medidas_Comercial.Recomendacion Estrategica ABC",
                "nativeQueryRef": "Recomendacion Estrategica ABC",
                "displayName": "Recomendación Estratégica"
            })
            d["visual"]["query"]["queryState"]["Values"]["projections"] = projs
            d["position"]["width"] = 640
            with open(abc_path, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            print("  + p3_pareto / v_tbl_abc actualizado con Recomendacion Estrategica ABC.")

    # 3. p2_precio / v_tbl_prc
    prc_path = os.path.join(pages_dir, "p2_precio", "visuals", "v_tbl_prc", "visual.json")
    if os.path.exists(prc_path):
        with open(prc_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        projs = [
            {
                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Productos"}}, "Property": "SKU"}},
                "queryRef": "Productos.SKU",
                "nativeQueryRef": "SKU",
                "displayName": "SKU"
            },
            {
                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Productos"}}, "Property": "Descripcion"}},
                "queryRef": "Productos.Descripcion",
                "nativeQueryRef": "Descripcion",
                "displayName": "Etiqueta Enológica"
            },
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Comercial"}}, "Property": "Precio Promedio Real"}},
                "queryRef": "_Medidas_Comercial.Precio Promedio Real",
                "nativeQueryRef": "Precio Promedio Real",
                "displayName": "Real ($)"
            },
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Comercial"}}, "Property": "Precio Promedio Presupuesto"}},
                "queryRef": "_Medidas_Comercial.Precio Promedio Presupuesto",
                "nativeQueryRef": "Precio Promedio Presupuesto",
                "displayName": "Plan ($)"
            },
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Comercial"}}, "Property": "Desvio Precio Promedio"}},
                "queryRef": "_Medidas_Comercial.Desvio Precio Promedio",
                "nativeQueryRef": "Desvio Precio Promedio",
                "displayName": "Desvío ($)"
            },
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Comercial"}}, "Property": "Semaforo Variacion Precio"}},
                "queryRef": "_Medidas_Comercial.Semaforo Variacion Precio",
                "nativeQueryRef": "Semaforo Variacion Precio",
                "displayName": "Semáforo Precio"
            },
            {
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Comercial"}}, "Property": "Regla Decision Precio"}},
                "queryRef": "_Medidas_Comercial.Regla Decision Precio",
                "nativeQueryRef": "Regla Decision Precio",
                "displayName": "Regla de Pricing"
            }
        ]
        d["visual"]["query"]["queryState"]["Values"]["projections"] = projs
        d["position"]["width"] = 640
        with open(prc_path, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, ensure_ascii=False)
        print("  + p2_precio / v_tbl_prc actualizado con Semaforo y Regla de Decision de Precio.")

def update_02_controller_matrices():
    print("\n--- Actualizando Matrices en 02_Control_de_Gestion ---")
    pages_dir = os.path.join(PORTFOLIO_DIR, "02_Control_de_Gestion", "Control_de_Gestion.Report", "definition", "pages")
    
    # 1. p2_ceco / v_tbl1
    ceco_tbl_path = os.path.join(pages_dir, "p2_ceco", "visuals", "v_tbl1", "visual.json")
    if os.path.exists(ceco_tbl_path):
        with open(ceco_tbl_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        projs = d["visual"]["query"]["queryState"]["Values"]["projections"]
        has_sem = any(p.get("nativeQueryRef") == "Alerta Semaforo OPEX" for p in projs)
        if not has_sem:
            projs.append({
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Controller"}}, "Property": "Alerta Semaforo OPEX"}},
                "queryRef": "_Medidas_Controller.Alerta Semaforo OPEX",
                "nativeQueryRef": "Alerta Semaforo OPEX",
                "displayName": "Semáforo OPEX"
            })
            d["visual"]["query"]["queryState"]["Values"]["projections"] = projs
            d["position"]["width"] = 520
            with open(ceco_tbl_path, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            print("  + p2_ceco / v_tbl1 actualizado con Alerta Semaforo OPEX.")

    # 2. p4_tesoreria / v_tbl_cobranzas
    tes_tbl_path = os.path.join(pages_dir, "p4_tesoreria", "visuals", "v_tbl_cobranzas", "visual.json")
    if os.path.exists(tes_tbl_path):
        with open(tes_tbl_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        projs = d["visual"]["query"]["queryState"]["Values"]["projections"]
        has_rec = any(p.get("nativeQueryRef") == "Recomendacion Cobertura" for p in projs)
        if not has_rec:
            projs.append({
                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Medidas_Tesoreria"}}, "Property": "Recomendacion Cobertura"}},
                "queryRef": "_Medidas_Tesoreria.Recomendacion Cobertura",
                "nativeQueryRef": "Recomendacion Cobertura",
                "displayName": "Cobertura Rofex Sugerida"
            })
            d["visual"]["query"]["queryState"]["Values"]["projections"] = projs
            d["position"]["width"] = 530
            with open(tes_tbl_path, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            print("  + p4_tesoreria / v_tbl_cobranzas actualizado con Recomendacion Cobertura Rofex.")

def update_06_riesgo_matrices():
    print("\n--- Actualizando Matrices en 06_Modelos_de_Riesgo_y_Prediccion ---")
    pages_dir = os.path.join(PORTFOLIO_DIR, "06_Modelos_de_Riesgo_y_Prediccion", "06_Modelos_de_Riesgo_y_Prediccion.Report", "definition", "pages")
    
    # p3_stress_testing_var / v_tbl_stress
    stress_path = os.path.join(pages_dir, "p3_stress_testing_var", "visuals", "v_tbl_stress", "visual.json")
    if os.path.exists(stress_path):
        with open(stress_path, "r", encoding="utf-8") as f:
            d = json.load(f)
        projs = d["visual"]["query"]["queryState"]["Values"]["projections"]
        has_sem = any(p.get("nativeQueryRef") == "Semaforo" for p in projs)
        if not has_sem:
            # Insertar antes de Prescripcion Directiva
            projs.insert(-1, {
                "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Riesgo_Reverse_Stress_Testing"}}, "Property": "Semaforo"}},
                "queryRef": "Riesgo_Reverse_Stress_Testing.Semaforo",
                "nativeQueryRef": "Semaforo",
                "displayName": "Semáforo Basilea"
            })
            d["visual"]["query"]["queryState"]["Values"]["projections"] = projs
            with open(stress_path, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            print("  + p3_stress_testing_var / v_tbl_stress actualizado con columna Semaforo Basilea.")

if __name__ == "__main__":
    update_04_operaciones_matrices()
    update_03_comercial_matrices()
    update_02_controller_matrices()
    update_06_riesgo_matrices()
    print("\n[ACTUALIZACION COMPLETA]: Todas las matrices analiticas enriquecidas con semaforos y reglas de decision.")
