# -*- coding: utf-8 -*-
"""
Elasticidad precio-demanda via regresion log-log con efectos fijos de
SKU y de mes-calendario (panel SKU x mes).

log(Volumen) = beta * log(Precio) + FE_sku + FE_mes + error

beta es la elasticidad-precio directamente (interpretacion: %cambio en
volumen ante 1% de cambio en precio, controlando por heterogeneidad de
producto y estacionalidad). Se reporta con error estandar y significancia
-- una elasticidad sin su intervalo de confianza no es un resultado
economico, es un numero suelto.
"""
import pandas as pd
import statsmodels.formula.api as smf


def estimar_elasticidad(panel: pd.DataFrame, log_vol_col="log_volumen",
                         log_precio_col="log_precio", sku_col="SKU", mes_col="Mes"):
    """
    panel: DataFrame con una fila por SKU x periodo. Debe contener columnas
    log(volumen), log(precio), SKU y mes-calendario (para efectos fijos).
    Devuelve el objeto de resultados de statsmodels (uso: .params, .bse,
    .pvalues, .rsquared, .summary()).
    """
    formula = f"{log_vol_col} ~ {log_precio_col} + C({sku_col}) + C({mes_col})"
    modelo = smf.ols(formula, data=panel).fit(cov_type="HC1")  # errores robustos a heterocedasticidad
    return modelo


def elasticidad_por_segmento(panel: pd.DataFrame, segmento_col="Segmento", **kwargs):
    """Corre la regresion por separado para cada segmento (Entrada/Reserva/Icono/etc)
    -- la elasticidad de un vino de entrada y uno icono no tienen por que
    ser iguales (bienes de necesidad vs. bienes de lujo/status)."""
    resultados = {}
    for seg, sub in panel.groupby(segmento_col):
        if sub[kwargs.get("sku_col", "SKU")].nunique() < 2:
            continue  # necesita variacion entre SKUs para los efectos fijos
        resultados[seg] = estimar_elasticidad(sub, **kwargs)
    return resultados


if __name__ == "__main__":
    import numpy as np
    rng = np.random.default_rng(0)
    n_sku, n_meses = 10, 36
    filas = []
    beta_real = -0.85
    for sku in range(n_sku):
        precio_base = rng.uniform(3000, 15000)
        for mes in range(n_meses):
            precio = precio_base * (1 + rng.normal(0, 0.05))
            log_precio = np.log(precio)
            log_vol = 5 + beta_real * log_precio + rng.normal(0, 0.1) + 0.3 * np.sin(2 * np.pi * mes / 12)
            filas.append({"SKU": f"SKU-{sku}", "Mes": mes % 12, "log_precio": log_precio, "log_volumen": log_vol})
    panel = pd.DataFrame(filas)
    modelo = estimar_elasticidad(panel)
    beta_estimado = modelo.params["log_precio"]
    print(f"Beta real simulado: {beta_real} | Beta estimado: {beta_estimado:.3f} | p-value: {modelo.pvalues['log_precio']:.4f}")
    assert abs(beta_estimado - beta_real) < 0.15, "el modelo deberia recuperar el beta real dentro de un margen razonable"
    print("OK: regresion de elasticidad recupera el parametro simulado correctamente")
