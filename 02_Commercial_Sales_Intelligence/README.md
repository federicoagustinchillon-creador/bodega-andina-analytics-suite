# 02_Commercial_Sales_Intelligence · Bodega & Agroindustria Andina S.A.

## Suite de Inteligencia Comercial, Rentabilidad Multicanal y Gestión de Portafolio ABC (Fabric Developer Mode - PBIP)
**Autor:** Federico Agustín Chillón  
**Afiliación Académica:** Facultad de Ciencias Económicas — Universidad Nacional de Cuyo (UNCUYO)  
**Capa de Datos:** `00_Data_Engineering_ETL/curated_gold`  
**Estándar Visual:** Deep Navy / Wine & Slate UXBIA (Lienzo `#0B1120`, Tarjetas `#131C31`, Acentos Borgoña `#9F1239` y Cian `#00A3FF`)  
**Periodo Fiscal:** 2025 · **Fecha de Corte:** 12/Septiembre/2026  

---

### 1. Visión General & Objetivos de Negocio

El proyecto **02_Commercial_Sales_Intelligence** proporciona a la Dirección Comercial, Gerencia de Ventas y al Controller Comercial una herramienta analítica avanzada para evaluar:
1. **Desempeño Multicanal:** Cumplimiento de cuotas presupuestadas, volumen físico en cajas, facturación real y ticket promedio en los 4 canales estratégicos (Exportación Directa, Distribuidores Mayoristas, Grandes Superficies / Supermercados y Canal On-Premise / HORECA).
2. **Dinámica de Precios vs. Listas Oficiales:** Monitoreo del precio medio ponderado por botella frente a la lista de precios presupuestada, detectando la erosión de margen por descuentos comerciales y bonificaciones.
3. **Gestión de Portafolio & Curva de Pareto 80/20:** Categorización ABC de productos bajo el principio de Vilfredo Pareto, identificando los SKUs tractores (Clase A), equilibradores (Clase B) y de rotación marginal (Clase C).

---

### 2. Arquitectura del Proyecto (PBIP / TMDL / PBIR)

Construido bajo el estándar **Power BI Project (`.pbip`)** de Microsoft Fabric:

```
02_Commercial_Sales_Intelligence/
|-- 02_Commercial_Sales_Intelligence.pbip
|-- 02_Commercial_Sales_Intelligence.SemanticModel/
|   |-- .platform
|   |-- definition.pbism
|   \-- definition/
|       |-- database.tmdl (Compatibility Level 1606)
|       |-- model.tmdl
|       |-- expressions.tmdl (Parámetro RutaDatos)
|       |-- relationships.tmdl (Relaciones 1:* limpias)
|       |-- cultures/en-US.tmdl
|       \-- tables/
|           |-- dim_calendario.tmdl
|           |-- dim_centros_costo.tmdl
|           |-- dim_productos.tmdl (SKU, Descripción, Línea, CategoriaABC)
|           |-- fact_ventas_reales.tmdl (Ventas granulares SAP SD)
|           |-- fact_presupuesto_ventas.tmdl (Metas comerciales unpivoteadas)
|           \-- _Medidas_Comercial.tmdl (40+ medidas DAX dinámicas)
\-- 02_Commercial_Sales_Intelligence.Report/
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
            |-- p1_multicanal/
            |-- p2_precios_lista/
            \-- p3_pareto_sku/
```

---

### 3. Modelo Semántico & Relaciones Star Schema

- `fact_ventas_reales[DateKey]` -> `dim_calendario[DateKey]` (N:1)
- `fact_ventas_reales[ProductoID]` -> `dim_productos[ProductoID]` (N:1)
- `fact_presupuesto_ventas[DateKey]` -> `dim_calendario[DateKey]` (N:1)
- `fact_presupuesto_ventas[ProductoID]` -> `dim_productos[ProductoID]` (N:1)
- `fact_presupuesto_ventas[CentroCostoID]` -> `dim_centros_costo[CentroCostoID]` (N:1)

---

### 4. Diccionario de Medidas DAX Dinámicas

#### Módulo 01: Ventas y Cumplimiento Multicanal
- `[Ingresos Reales]`: Suma de facturación neta de impuestos en ARS ($).
- `[Volumen Real]`: Cantidad física de cajas de 6/12 unidades vendidas.
- `[Cumplimiento Presupuesto %]`: `DIVIDE([Ingresos Reales], [Ingresos Presupuesto], 0)`.
- `[Desvío Cuota %]`: `DIVIDE([Ingresos Reales] - [Ingresos Presupuesto], [Ingresos Presupuesto], 0)`.
- `[Ticket Promedio]`: `DIVIDE([Ingresos Reales], [Cantidad Pedidos], 0)`.

#### Módulo 02: Precios, Descuentos y Margen de Contribución
- `[Precio Promedio Real]`: `DIVIDE([Ingresos Reales], [Volumen Real], 0)`.
- `[Precio Lista Presupuestado]`: `DIVIDE([Ingresos Presupuesto], [Volumen Presupuesto], 0)`.
- `[Desvío de Precio $]`: `[Precio Promedio Real] - [Precio Lista Presupuestado]`.
- `[Descuento Comercial Promedio %]`: `DIVIDE([Precio Lista Presupuestado] - [Precio Promedio Real], [Precio Lista Presupuestado], 0)`.
- `[Margen Bruto %]`: `DIVIDE([Margen Bruto Real], [Ingresos Reales], 0)`.

#### Módulo 03: Concentración de Cartera y Pareto ABC
- `[Ventas Acumuladas %]`: Cálculo dinámico de la curva de Lorenz sobre el catálogo de productos.
- `[SKUs Clase A]`: Conteo de etiquetas que componen el 80% de la facturación.
- `[Ingresos Clase A]`: Facturación total proveniente de SKUs Clase A.
- `[Concentración Top 2 Productos %]`: Ratio de facturación de las dos etiquetas insignia de la bodega.

---

### 5. Estándar Visual y Ergonomía Cognitiva

- **Lienzo Principal:** `#0B1120` con fondo oscuro libre de reflejos y óptimo para salas de directorio.
- **Sidebar de Filtros (x: 0, w: 200):** Selectores en dropdown (Año, Mes, Canal, Línea Enológica, SKU), botón interactivo de reseteo y bloque de gobernanza de datos.
- **Header Superior (x: 212, y: 12, w: 1056, h: 48):** Título formal, subtítulo analítico y pestañas pastilla (`[● 1. Multicanal] [○ 2. Dinámica Precios] [○ 3. Portafolio & Pareto]`).
- **Fila KPI (y: 66, h: 88):** 4 tarjetas con callout grande de 20pt `#F8FAFC`, contenedor `#131C31` y borde sutil `#1E293B`.
- **Cuadrícula Analítica (Upper y: 162 | Lower y: 427):** 4 visuales interactivos por página (gráficos combinados de barras y líneas, matrices de márgenes y tablas de alertas). Cero solapamientos.
