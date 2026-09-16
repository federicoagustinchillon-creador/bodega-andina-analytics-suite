# -*- coding: utf-8 -*-
"""
Expande raw_presupuesto_horizontal.csv de 8 a 36 SKUs (catalogo actual),
manteniendo el esquema horizontal original (Presupuesto FY2025, 2 centros de
costo por SKU: CC-202 domestico, CC-203 mayorista/export). Volumen mensual
calibrado con el indice estacional real INV 2024 (mismo usado en el motor
econometrico) para que Budget y Actual compartan la misma forma estacional
de negocio, con una desviacion aleatoria realista (para que existan variances
Budget vs Actual, que es justamente lo que la pagina de Controller analiza).
"""
import numpy as np
import pandas as pd
from pathlib import Path

RNG = np.random.default_rng(11)
BASE_DIR = Path(__file__).resolve().parent
REAL_DIR = BASE_DIR.parent / "Analisis_Econometrico" / "data" / "real"

MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

VOL_BASE_POR_SEGMENTO = {
    "Entrada": 6200,
    "Reserva": 4300,
    "Gran Reserva / Icono": 900,
    "Espumante": 2600,
    "Granel / Masivo": 18000,
}


def cargar_catalogo():
    return pd.read_csv(BASE_DIR / "raw" / "raw_maestro_productos.csv")


def cargar_indice_estacional():
    idx = pd.read_csv(REAL_DIR / "indice_estacional_inv_2024.csv", index_col="mes")["indice_estacional_2024_real"]
    return {i: idx.loc[i] for i in range(1, 13)}


def generar():
    catalogo = cargar_catalogo()
    idx_est = cargar_indice_estacional()

    filas = []
    for _, prod in catalogo.iterrows():
        vol_base = VOL_BASE_POR_SEGMENTO[prod["Segmento"]]
        precio = prod["PrecioPresupuestadoUnit"]

        for cc, share in [("CC-202", 0.62), ("CC-203", 0.38)]:
            fila = {"ProductoID": prod["ProductoID"], "CentroCostoID": cc}
            for mes_num, mes_abbr in enumerate(MESES, start=1):
                estacional = idx_est[mes_num]
                ruido = 1 + RNG.normal(0, 0.05)
                vol = max(1, round(vol_base * share * estacional * ruido))
                precio_mes = precio * (1 + RNG.normal(0, 0.02))
                ing = round(vol * precio_mes, 1)
                fila[f"{mes_abbr}_Vol"] = int(vol)
                fila[f"{mes_abbr}_Ing"] = ing
            filas.append(fila)

    return pd.DataFrame(filas)


if __name__ == "__main__":
    df = generar()
    df.to_csv(BASE_DIR / "raw" / "raw_presupuesto_horizontal.csv", index=False)
    print(f"raw_presupuesto_horizontal.csv: {df.shape[0]} filas ({df['ProductoID'].nunique()} SKUs x 2 CC)")
