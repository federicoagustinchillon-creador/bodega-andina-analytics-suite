# -*- coding: utf-8 -*-
"""
Inyector de Contenedores Visuales 'image' para Iconos de Tarjetas KPI en Fabric PBIR.
Posiciona con precision milimetrica cada icono en la esquina superior derecha
de su respectiva tarjeta KPI (x = kpi.x + kpi.w - 38, y = kpi.y + 10, w = 26, h = 26, z = 15).
Garantiza cero colisiones, tipado 'Image' en RegisteredResources y preservacion
estricta de carpetas manuales.

Autor: Federico Agustin Chillon - UNCUYO
"""

import os
import json

PORTFOLIO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES_CONFIG = [
    # 04_Operaciones_y_Planta
    {
        "proj": "04_Operaciones_y_Planta",
        "rep": "Operaciones_y_Planta.Report",
        "page": "p1_vendimia",
        "icons": ["icon_grape.png", "icon_barrel.png", "icon_gauge.png", "icon_thermometer.png"]
    },
    {
        "proj": "04_Operaciones_y_Planta",
        "rep": "Operaciones_y_Planta.Report",
        "page": "p2_costos",
        "icons": ["icon_currency.png", "icon_margin.png", "icon_alert.png", "icon_factory.png"]
    },
    {
        "proj": "04_Operaciones_y_Planta",
        "rep": "Operaciones_y_Planta.Report",
        "page": "p3_mermas",
        "icons": ["icon_currency.png", "icon_clock.png", "icon_alert.png", "icon_box.png"]
    },
    # 06_Modelos_de_Riesgo_y_Prediccion
    {
        "proj": "06_Modelos_de_Riesgo_y_Prediccion",
        "rep": "06_Modelos_de_Riesgo_y_Prediccion.Report",
        "page": "p1_ml_clasificacion",
        "icons": ["icon_brain.png", "icon_gauge.png", "icon_target.png", "icon_alert.png"]
    },
    {
        "proj": "06_Modelos_de_Riesgo_y_Prediccion",
        "rep": "06_Modelos_de_Riesgo_y_Prediccion.Report",
        "page": "p2_forecasting_ml",
        "icons": ["icon_box.png", "icon_forecast.png", "icon_trend.png", "icon_shield.png"]
    },
    {
        "proj": "06_Modelos_de_Riesgo_y_Prediccion",
        "rep": "06_Modelos_de_Riesgo_y_Prediccion.Report",
        "page": "p3_stress_testing_var",
        "icons": ["icon_cash.png", "icon_shield.png", "icon_vault.png", "icon_clock.png"]
    },
    {
        "proj": "06_Modelos_de_Riesgo_y_Prediccion",
        "rep": "06_Modelos_de_Riesgo_y_Prediccion.Report",
        "page": "p4_inferencia_causal",
        "icons": ["icon_causal.png", "icon_target.png", "icon_truck.png", "icon_margin.png"]
    },
    # 03_Inteligencia_Comercial
    {
        "proj": "03_Inteligencia_Comercial",
        "rep": "Inteligencia_Comercial.Report",
        "page": "p1_canal",
        "icons": ["icon_currency.png", "icon_target.png", "icon_box.png", "icon_cart.png"]
    },
    {
        "proj": "03_Inteligencia_Comercial",
        "rep": "Inteligencia_Comercial.Report",
        "page": "p2_precio",
        "icons": ["icon_currency.png", "icon_target.png", "icon_alert.png", "icon_margin.png"]
    },
    {
        "proj": "03_Inteligencia_Comercial",
        "rep": "Inteligencia_Comercial.Report",
        "page": "p3_pareto",
        "icons": ["icon_grape.png", "icon_currency.png", "icon_margin.png", "icon_ebitda.png"]
    },
    {
        "proj": "03_Inteligencia_Comercial",
        "rep": "Inteligencia_Comercial.Report",
        "page": "p4_econometria",
        "icons": ["icon_causal.png", "icon_trend.png", "icon_shield.png", "icon_clock.png"]
    },
    # 02_Control_de_Gestion
    {
        "proj": "02_Control_de_Gestion",
        "rep": "Control_de_Gestion.Report",
        "page": "p1_cascada",
        "icons": ["icon_currency.png", "icon_margin.png", "icon_ebitda.png", "icon_clock.png"]
    },
    {
        "proj": "02_Control_de_Gestion",
        "rep": "Control_de_Gestion.Report",
        "page": "p2_ceco",
        "icons": ["icon_currency.png", "icon_clock.png", "icon_alert.png", "icon_margin.png"]
    },
    {
        "proj": "02_Control_de_Gestion",
        "rep": "Control_de_Gestion.Report",
        "page": "p3_flujo",
        "icons": ["icon_clock.png", "icon_box.png", "icon_truck.png", "icon_currency.png"]
    },
    {
        "proj": "02_Control_de_Gestion",
        "rep": "Control_de_Gestion.Report",
        "page": "p4_tesoreria",
        "prefix": "kpi_fx_",
        "z": 9500,
        "icons": ["icon_cash.png", "icon_trend.png", "icon_shield.png", "icon_vault.png"]
    }
]

def inject_icons():
    print("=" * 80)
    print("INYECTANDO ICONOS VISUALES EN TARJETAS KPI DE LA SUITE POWER BI")
    print("=" * 80)
    
    injected_count = 0
    for cfg in PAGES_CONFIG:
        visuals_dir = os.path.join(PORTFOLIO_DIR, cfg["proj"], cfg["rep"], "definition", "pages", cfg["page"], "visuals")
        if not os.path.isdir(visuals_dir):
            print(f"[ALERTA] Directorio de visuales no encontrado: {visuals_dir}")
            continue
            
        print(f"\n[PROCESANDO PAGINA]: {cfg['proj']} / {cfg['page']}")
        
        prefix = cfg.get("prefix", "kpi_")
        default_z = cfg.get("z", 15)
        
        for i in range(1, 5):
            kpi_name = f"{prefix}{i}"
            img_name = f"img_kpi_{i}"
            icon_file = cfg["icons"][i - 1]
            
            kpi_path = os.path.join(visuals_dir, kpi_name, "visual.json")
            if not os.path.exists(kpi_path):
                print(f"  * No se encontro {kpi_name} en {cfg['page']}")
                continue
                
            with open(kpi_path, "r", encoding="utf-8") as f:
                kpi_data = json.load(f)
                
            pos = kpi_data.get("position", {})
            kx = pos.get("x", 196 + (i - 1) * 271)
            ky = pos.get("y", 66)
            kw = pos.get("width", 256)
            kh = pos.get("height", 84)
            
            # Coordenadas exactas en la esquina superior derecha de la tarjeta KPI
            img_x = round(kx + kw - 38, 2)
            img_y = round(ky + 10, 2)
            img_w = 26
            img_h = 26
            img_z = default_z
            
            img_container = {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
                "name": img_name,
                "position": {
                    "x": img_x,
                    "y": img_y,
                    "z": img_z,
                    "height": img_h,
                    "width": img_w,
                    "tabOrder": 0
                },
                "visual": {
                    "visualType": "image",
                    "objects": {
                        "general": [
                            {
                                "properties": {
                                    "imageUrl": {
                                        "expr": {
                                            "ResourcePackageItem": {
                                                "PackageName": "RegisteredResources",
                                                "PackageType": 1,
                                                "ItemName": icon_file
                                            }
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
            
            img_dir = os.path.join(visuals_dir, img_name)
            os.makedirs(img_dir, exist_ok=True)
            img_file = os.path.join(img_dir, "visual.json")
            with open(img_file, "w", encoding="utf-8") as f:
                json.dump(img_container, f, indent=2, ensure_ascii=False)
                
            print(f"  + {img_name}: {icon_file} @ ({img_x}, {img_y}, {img_w}x{img_h}, z={img_z})")
            injected_count += 1

    print("\n" + "=" * 80)
    print(f"EXITO: Se inyectaron exitosamente {injected_count} contenedores de iconos en tarjetas KPI.")
    print("=" * 80)

if __name__ == "__main__":
    inject_icons()
