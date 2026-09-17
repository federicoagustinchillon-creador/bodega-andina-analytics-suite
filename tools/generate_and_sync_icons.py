# -*- coding: utf-8 -*-
"""
Generador Maestro y Sincronizador de Iconos Ejecutivos UXBIA.
Genera iconos vectoriales/rasterizados en alta resolucion (512x512) y los reduce
con filtro Lanczos a 128x128 RGBA para anti-aliasing impecable sobre badges
circulares translucidos corporativos (#0EA5E9 / #38BDF8).

Distribuye el catalogo completo de 21 iconos en los 4 proyectos Power BI
y actualiza sus respectivos 'report.json' con registro formal Fabric 'Image'.

Autor: Federico Agustin Chillon - UNCUYO
"""

import os
import json
import math
from PIL import Image, ImageDraw

PORTFOLIO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS = [
    ("02_Control_de_Gestion", "Control_de_Gestion.Report"),
    ("03_Inteligencia_Comercial", "Inteligencia_Comercial.Report"),
    ("04_Operaciones_y_Planta", "Operaciones_y_Planta.Report"),
    ("06_Modelos_de_Riesgo_y_Prediccion", "06_Modelos_de_Riesgo_y_Prediccion.Report")
]

S = 512
SCALE = S / 128.0

def make_base():
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx, cy = S // 2, S // 2
    r = int(56 * SCALE)
    # Fondo circular translucido cyan UXBIA
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=(14, 165, 233, 40),
                 outline=(56, 189, 248, 190),
                 width=int(2.8 * SCALE))
    return img, draw

CYAN = (56, 189, 248, 255)
WHITE = (248, 250, 252, 255)
EMERALD = (16, 185, 129, 255)
AMBER = (245, 158, 11, 255)
ROSE = (244, 63, 94, 255)
SLATE = (148, 163, 184, 220)

def generate_new_icons():
    new_icons = {}

    # 1. icon_shield.png (Solvencia, Basilea III, Reverse Stress)
    img, draw = make_base()
    pts = [
        (64*SCALE, 28*SCALE),
        (94*SCALE, 40*SCALE),
        (88*SCALE, 76*SCALE),
        (64*SCALE, 98*SCALE),
        (40*SCALE, 76*SCALE),
        (34*SCALE, 40*SCALE)
    ]
    draw.polygon(pts, fill=(16, 185, 129, 50), outline=EMERALD)
    check = [
        (48*SCALE, 62*SCALE),
        (58*SCALE, 74*SCALE),
        (80*SCALE, 48*SCALE)
    ]
    draw.line(check, fill=WHITE, width=int(3.5*SCALE), joint='curve')
    new_icons['icon_shield.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    # 2. icon_trend.png (Tendencia financiera y proyeccion ascendente)
    img, draw = make_base()
    draw.line([(36*SCALE, 92*SCALE), (92*SCALE, 92*SCALE)], fill=SLATE, width=int(2*SCALE))
    draw.line([(36*SCALE, 92*SCALE), (36*SCALE, 36*SCALE)], fill=SLATE, width=int(2*SCALE))
    trend_pts = [
        (42*SCALE, 82*SCALE),
        (56*SCALE, 70*SCALE),
        (70*SCALE, 58*SCALE),
        (88*SCALE, 42*SCALE)
    ]
    draw.line(trend_pts, fill=CYAN, width=int(3.5*SCALE), joint='curve')
    arrow = [(76*SCALE, 42*SCALE), (88*SCALE, 42*SCALE), (88*SCALE, 54*SCALE)]
    draw.line(arrow, fill=CYAN, width=int(3.5*SCALE), joint='curve')
    for pt in trend_pts:
        draw.ellipse([pt[0]-3*SCALE, pt[1]-3*SCALE, pt[0]+3*SCALE, pt[1]+3*SCALE], fill=WHITE)
    new_icons['icon_trend.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    # 3. icon_brain.png (Redes neuronales, algoritmos y Machine Learning)
    img, draw = make_base()
    inputs = [(44*SCALE, 52*SCALE), (44*SCALE, 76*SCALE)]
    hidden = [(64*SCALE, 40*SCALE), (64*SCALE, 64*SCALE), (64*SCALE, 88*SCALE)]
    outputs = [(84*SCALE, 52*SCALE), (84*SCALE, 76*SCALE)]
    for inp in inputs:
        for hid in hidden:
            draw.line([inp, hid], fill=(56, 189, 248, 120), width=int(1.5*SCALE))
    for hid in hidden:
        for out in outputs:
            draw.line([hid, out], fill=(56, 189, 248, 120), width=int(1.5*SCALE))
    for inp in inputs:
        draw.ellipse([inp[0]-4*SCALE, inp[1]-4*SCALE, inp[0]+4*SCALE, inp[1]+4*SCALE], fill=CYAN, outline=WHITE, width=int(1*SCALE))
    for hid in hidden:
        draw.ellipse([hid[0]-4.5*SCALE, hid[1]-4.5*SCALE, hid[0]+4.5*SCALE, hid[1]+4.5*SCALE], fill=EMERALD, outline=WHITE, width=int(1*SCALE))
    for out in outputs:
        draw.ellipse([out[0]-4*SCALE, out[1]-4*SCALE, out[0]+4*SCALE, out[1]+4*SCALE], fill=AMBER, outline=WHITE, width=int(1*SCALE))
    new_icons['icon_brain.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    # 4. icon_forecast.png (Forecasting de demanda, cono de incertidumbre)
    img, draw = make_base()
    draw.line([(36*SCALE, 92*SCALE), (92*SCALE, 92*SCALE)], fill=SLATE, width=int(2*SCALE))
    draw.line([(36*SCALE, 92*SCALE), (36*SCALE, 36*SCALE)], fill=SLATE, width=int(2*SCALE))
    hist_pts = [(40*SCALE, 78*SCALE), (52*SCALE, 66*SCALE), (64*SCALE, 72*SCALE)]
    draw.line(hist_pts, fill=WHITE, width=int(3*SCALE), joint='curve')
    cone_pts = [(64*SCALE, 72*SCALE), (88*SCALE, 44*SCALE), (88*SCALE, 66*SCALE)]
    draw.polygon(cone_pts, fill=(56, 189, 248, 60))
    fc_pts = [(64*SCALE, 72*SCALE), (76*SCALE, 58*SCALE), (88*SCALE, 54*SCALE)]
    draw.line(fc_pts, fill=CYAN, width=int(3*SCALE), joint='curve')
    draw.line([(64*SCALE, 38*SCALE), (64*SCALE, 90*SCALE)], fill=AMBER, width=int(1.5*SCALE))
    new_icons['icon_forecast.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    # 5. icon_target.png (Diana, Youden J y meta de cuota)
    img, draw = make_base()
    cx, cy = S // 2, S // 2
    draw.ellipse([cx - 28*SCALE, cy - 28*SCALE, cx + 28*SCALE, cy + 28*SCALE], outline=CYAN, width=int(2.5*SCALE))
    draw.ellipse([cx - 18*SCALE, cy - 18*SCALE, cx + 18*SCALE, cy + 18*SCALE], outline=WHITE, width=int(2*SCALE))
    draw.ellipse([cx - 7*SCALE, cy - 7*SCALE, cx + 7*SCALE, cy + 7*SCALE], fill=AMBER, outline=WHITE, width=int(1*SCALE))
    draw.line([(cx - 34*SCALE, cy), (cx - 22*SCALE, cy)], fill=CYAN, width=int(2*SCALE))
    draw.line([(cx + 22*SCALE, cy), (cx + 34*SCALE, cy)], fill=CYAN, width=int(2*SCALE))
    draw.line([(cx, cy - 34*SCALE), (cx, cy - 22*SCALE)], fill=CYAN, width=int(2*SCALE))
    draw.line([(cx, cy + 22*SCALE), (cx, cy + 34*SCALE)], fill=CYAN, width=int(2*SCALE))
    new_icons['icon_target.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    # 6. icon_gauge.png (Eficiencia de planta y accuracy %)
    img, draw = make_base()
    cx, cy = S // 2, int(68 * SCALE)
    r_gauge = int(28 * SCALE)
    draw.arc([cx - r_gauge, cy - r_gauge, cx + r_gauge, cy + r_gauge], start=180, end=0, fill=CYAN, width=int(3.5*SCALE))
    needle_angle = math.radians(45)
    nx = cx + int(20 * SCALE * math.cos(needle_angle))
    ny = cy - int(20 * SCALE * math.sin(needle_angle))
    draw.line([(cx, cy), (nx, ny)], fill=EMERALD, width=int(3*SCALE))
    draw.ellipse([cx - 4*SCALE, cy - 4*SCALE, cx + 4*SCALE, cy + 4*SCALE], fill=WHITE)
    new_icons['icon_gauge.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    # 7. icon_cash.png (Billetes / Liquidez Miller-Orr)
    img, draw = make_base()
    draw.rectangle([38*SCALE, 52*SCALE, 86*SCALE, 80*SCALE], fill=(16, 185, 129, 60), outline=EMERALD, width=int(2.5*SCALE))
    draw.rectangle([42*SCALE, 44*SCALE, 90*SCALE, 72*SCALE], fill=(16, 185, 129, 80), outline=EMERALD, width=int(2.5*SCALE))
    draw.rectangle([46*SCALE, 36*SCALE, 94*SCALE, 64*SCALE], fill=(16, 185, 129, 120), outline=WHITE, width=int(2.5*SCALE))
    draw.ellipse([65*SCALE, 45*SCALE, 75*SCALE, 55*SCALE], outline=WHITE, width=int(1.5*SCALE))
    new_icons['icon_cash.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    # 8. icon_vault.png (Caja fuerte / Buffer de solvencia contingente)
    img, draw = make_base()
    draw.rounded_rectangle([36*SCALE, 36*SCALE, 92*SCALE, 92*SCALE], radius=int(6*SCALE), fill=(15, 23, 42, 180), outline=CYAN, width=int(3*SCALE))
    cx, cy = S // 2, S // 2
    draw.ellipse([cx - 14*SCALE, cy - 14*SCALE, cx + 14*SCALE, cy + 14*SCALE], outline=AMBER, width=int(2.5*SCALE))
    draw.ellipse([cx - 4*SCALE, cy - 4*SCALE, cx + 4*SCALE, cy + 4*SCALE], fill=WHITE)
    for deg in [0, 60, 120, 180, 240, 300]:
        rad = math.radians(deg)
        sp_x1 = cx + int(6 * SCALE * math.cos(rad))
        sp_y1 = cy + int(6 * SCALE * math.sin(rad))
        sp_x2 = cx + int(14 * SCALE * math.cos(rad))
        sp_y2 = cy + int(14 * SCALE * math.sin(rad))
        draw.line([(sp_x1, sp_y1), (sp_x2, sp_y2)], fill=AMBER, width=int(2*SCALE))
    new_icons['icon_vault.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    # 9. icon_causal.png (DAG Inferencia Causal DML)
    img, draw = make_base()
    w_node = (64*SCALE, 38*SCALE)
    x_node = (44*SCALE, 80*SCALE)
    y_node = (84*SCALE, 80*SCALE)
    draw.line([w_node, x_node], fill=SLATE, width=int(2*SCALE))
    draw.line([w_node, y_node], fill=SLATE, width=int(2*SCALE))
    draw.line([x_node, y_node], fill=CYAN, width=int(3.5*SCALE))
    draw.polygon([(76*SCALE, 77*SCALE), (84*SCALE, 80*SCALE), (76*SCALE, 83*SCALE)], fill=CYAN)
    draw.ellipse([w_node[0]-6*SCALE, w_node[1]-6*SCALE, w_node[0]+6*SCALE, w_node[1]+6*SCALE], fill=AMBER, outline=WHITE, width=int(1.5*SCALE))
    draw.ellipse([x_node[0]-6.5*SCALE, x_node[1]-6.5*SCALE, x_node[0]+6.5*SCALE, x_node[1]+6.5*SCALE], fill=CYAN, outline=WHITE, width=int(1.5*SCALE))
    draw.ellipse([y_node[0]-6.5*SCALE, y_node[1]-6.5*SCALE, y_node[0]+6.5*SCALE, y_node[1]+6.5*SCALE], fill=EMERALD, outline=WHITE, width=int(1.5*SCALE))
    new_icons['icon_causal.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    # 10. icon_thermometer.png (Refractómetro / Grados Brix Vendimia)
    img, draw = make_base()
    cx = S // 2
    draw.rounded_rectangle([cx - 4*SCALE, 34*SCALE, cx + 4*SCALE, 76*SCALE], radius=int(3*SCALE), fill=(56, 189, 248, 60), outline=WHITE, width=int(2*SCALE))
    draw.ellipse([cx - 10*SCALE, 70*SCALE, cx + 10*SCALE, 90*SCALE], fill=ROSE, outline=WHITE, width=int(2*SCALE))
    draw.rectangle([cx - 2.5*SCALE, 48*SCALE, cx + 2.5*SCALE, 72*SCALE], fill=ROSE)
    for y_mark in [42, 50, 58, 66]:
        draw.line([(cx + 6*SCALE, y_mark*SCALE), (cx + 10*SCALE, y_mark*SCALE)], fill=CYAN, width=int(1.5*SCALE))
    new_icons['icon_thermometer.png'] = img.resize((128, 128), Image.Resampling.LANCZOS)

    return new_icons

def sync_all_icons_and_reports():
    new_icons = generate_new_icons()
    
    # Directorio fuente maestro de iconos existentes (04_Operaciones_y_Planta)
    src_res_dir = os.path.join(PORTFOLIO_DIR, "04_Operaciones_y_Planta", "Operaciones_y_Planta.Report", "StaticResources", "RegisteredResources")
    
    # Guardar los 10 nuevos iconos en el directorio fuente maestro
    for name, img in new_icons.items():
        dst_path = os.path.join(src_res_dir, name)
        img.save(dst_path, format="PNG")
        print(f"[NUEVO ICONO CREADO]: {name} -> {dst_path}")
        
    # Obtener el conjunto total de archivos PNG de iconos
    all_icons = sorted([f for f in os.listdir(src_res_dir) if f.startswith("icon_") and f.endswith(".png")])
    print(f"\n[CATALOGO TOTAL DE ICONOS]: {len(all_icons)} iconos encontrados")
    for ic in all_icons:
        print(f"  - {ic}")
        
    # Sincronizar hacia los 4 reportes
    for proj, rep in PROJECTS:
        rep_dir = os.path.join(PORTFOLIO_DIR, proj, rep)
        res_dir = os.path.join(rep_dir, "StaticResources", "RegisteredResources")
        os.makedirs(res_dir, exist_ok=True)
        
        # Copiar todos los iconos
        for ic in all_icons:
            src = os.path.join(src_res_dir, ic)
            dst = os.path.join(res_dir, ic)
            if src != dst:
                with open(src, "rb") as sf, open(dst, "wb") as df:
                    df.write(sf.read())
                    
        # Actualizar report.json
        rep_json_path = os.path.join(rep_dir, "definition", "report.json")
        if os.path.exists(rep_json_path):
            with open(rep_json_path, "r", encoding="utf-8") as f:
                rep_data = json.load(f)
                
            pkg_list = rep_data.get("resourcePackages", [])
            reg_pkg = None
            for p in pkg_list:
                if p.get("name") == "RegisteredResources":
                    reg_pkg = p
                    break
            if not reg_pkg:
                reg_pkg = {"name": "RegisteredResources", "type": "RegisteredResources", "items": []}
                pkg_list.append(reg_pkg)
                rep_data["resourcePackages"] = pkg_list
                
            # Mantener custom themes y otros items existentes que no sean iconos
            items = [it for it in reg_pkg.get("items", []) if not it.get("name", "").startswith("icon_")]
            # Agregar todos los iconos como Image
            for ic in all_icons:
                items.append({
                    "name": ic,
                    "path": ic,
                    "type": "Image"
                })
            reg_pkg["items"] = items
            
            with open(rep_json_path, "w", encoding="utf-8") as f:
                json.dump(rep_data, f, indent=2, ensure_ascii=False)
            print(f"[REPORT.JSON ACTUALIZADO]: {rep_json_path} con {len(items)} items registrados")

if __name__ == "__main__":
    sync_all_icons_and_reports()
