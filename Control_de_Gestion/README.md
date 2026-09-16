# Control_de_Gestion · Bodega & Agroindustria Andina S.A.

## Suite de Inteligencia de Negocios y Control Financiero (Fabric Developer Mode - PBIP)
**Autor:** Federico Agustín Chillón, UNCUYO  
**Capa de Datos:** `Ingenieria_de_Datos/curated_gold`  
**Estándar Visual:** Deep Navy / Wine & Slate UXBIA  
**Periodo Fiscal:** 2025 · **Fecha de Corte:** 12/Septiembre/2026  

---

### 1. Arquitectura del Proyecto

El proyecto está diseñado bajo la arquitectura abierta **PBIP** (Fabric Developer Mode) con separación estricta entre el modelo semántico en **TMDL** y el reporte en **PBIR**:

```
Control_de_Gestion/
|-- Control_de_Gestion.pbip
|-- Control_de_Gestion.SemanticModel/
|   |-- .platform
|   |-- definition.pbism
|   \-- definition/
|       |-- database.tmdl (Compat Level 1606)
|       |-- model.tmdl
|       |-- expressions.tmdl (Parámetro RutaDatos)
|       |-- relationships.tmdl (Relaciones 1:* limpias)
|       |-- cultures/en-US.tmdl
|       \-- tables/
|           |-- dim_calendario.tmdl
|           |-- dim_centros_costo.tmdl
|           |-- dim_cuentas_contables.tmdl
|           |-- dim_productos.tmdl
|           |-- fact_ventas_reales.tmdl
|           |-- fact_presupuesto_ventas.tmdl
|           |-- fact_opex_mensual.tmdl
|           |-- fact_capital_trabajo.tmdl
|           |-- dim_desglose_cascada.tmdl
|           \-- _Medidas_Controller.tmdl (56 medidas DAX dinámicas)
\-- Control_de_Gestion.Report/
    |-- .platform
    |-- definition.pbir
    |-- StaticResources/
    |   \-- RegisteredResources/
    |       \-- Deep_Navy_UXBIA_Theme.json
    \-- definition/
        |-- report.json
        |-- version.json
        \-- pages/
            |-- pages.json
            |-- p1_pl_cascada/
            |-- p2_centros_costo/
            \-- p3_liquidez_flujo/
```

---

### 2. Estándar de Diseño UXBIA (Deep Navy / Wine & Slate)

- **Canvas Background:** `#0B1120` (Navy Oscuro Profundo).
- **Sidebar FILTERS (Izquierda):** `#121826` con borde derecho `1px solid #1E2638`, ancho `200px`. Contiene selectores dinámicos de Año, Mes, Línea de Vino, Canal Comercial, y badge institucional.
- **Top Tabs Container:** `#121826`, pestaña activa `#1E2A45` con indicador azul eléctrico `#00A3FF`.
- **Cards y Paneles:** `#131C31` con borde `1px solid #1E293B`, radio de esquina `8px`.
- **Acentos Cromáticos:** Borgoña Malbec `#9F1239` y Azul Cian Eléctrico `#0EA5E9`.
- **Tipografía:** Segoe UI con alineación tabular estricta y formato contable institucional.

---

### 3. Modelo DAX y Descomposición Ortogonal de Desvíos (Variance Analysis)

Todas las medidas han sido desarrolladas con cero hardcoding, empleando agregaciones dinámicas sobre las tablas transaccionales del modelo.

#### Reconciliación de Margen Bruto:
$$\Delta Margen = Margen_{Real} - Margen_{Plan}$$
$$EV = \sum (Q_{Real} - Q_{Plan}) \times (P_{Plan} - C_{Plan})$$
$$EP = \sum Q_{Real} \times (P_{Real} - P_{Plan})$$
$$EC = \sum Q_{Real} \times (C_{Plan} - C_{Real})$$
$$\text{Cuadratura Exacta} = \Delta Margen - (EV + EP + EC) = \$0.00$$

#### Resumen Global de Cuadratura (Año Fiscal 2025):
- **Margen Bruto Presupuestado:** $2,614,800,100.00
- **Efecto Volumen (EV):** -$1,873,664,800.00
- **Efecto Precio (EP):** +$35,127,586.80
- **Efecto Costo (EC):** -$7,615,194.70
- **Margen Bruto Real:** $768,647,692.10
- **Diferencia de Cuadratura:** $0.00 exacto

---

### 4. Páginas del Reporte

1. **`p1_pl_cascada` - P&L Ejecutivo & Descomposición de Desvíos:**
   - 4 KPI Cards: Ingresos Netos Reales, Margen Bruto Real, EBITDA Operativo, Ciclo Efectivo (CCC).
   - Fila Superior: Waterfall Chart de Variance Analysis (Margen Plan -> EV -> EP -> EC -> Margen Real) y Gráfico de Barras Horizontales de Margen Bruto % Real vs Plan por Línea.
   - Fila Inferior: Matriz analítica de rentabilidad y desvíos por SKU y Panel Ejecutivo de Conclusiones FP&A.

2. **`p2_centros_costo` - Control Presupuestario OPEX (SAP CO-CCA):**
   - 4 KPI Cards: OPEX Real Total, OPEX Presupuesto, Desvío Presupuestario OPEX, Ratio OPEX / Ingresos.
   - Fila Superior: Gráfico de barras horizontales de ejecución por Centro de Costo (CC-101 a CC-203) y Gráfico de Columnas de Desglose de OPEX por Cuenta Contable (SAP FI).
   - Fila Inferior: Tabla de Alertas Presupuestarias con semáforo de tolerancia condicional y Panel Ejecutivo de Contención del Gasto.

3. **`p3_liquidez_flujo` - Capital de Trabajo & Flujo de Caja Operativo:**
   - 5 KPI Cards: DSO Cobro, DIO Inventario, DPO Pago, Ciclo Neto (CCC), NOF Requerida.
   - Fila Superior: Gráfico multi-línea de evolución mensual de días de rotación (DSO, DIO, DPO y CCC) y Gráfico de Columnas de Composición de NOF (CxC + Inventarios vs CxP).
   - Fila Inferior: Detalle Mensual de Liquidez, Capital de Trabajo y Cobertura Operativa, y Panel de Síntesis Estratégica bajo Pirámide de Minto.
