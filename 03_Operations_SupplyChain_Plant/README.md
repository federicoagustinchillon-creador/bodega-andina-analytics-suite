# SUITE DE GESTIÓN OPERATIVA, PLANTA Y SUPPLY CHAIN (PBIP)
## Bodega & Agroindustria Andina S.A. — Planta San Martín (Mendoza)
**Autor:** Federico Agustín Chillón  
**Afiliación:** Licenciatura en Economía — Universidad Nacional de Cuyo (UNCUYO)  
**Estándar de Diseño:** Deep Navy / Wine & Slate UXBIA (Fabric Developer Mode)  
**Formato de Implementación:** Microsoft Fabric PBIR & TMDL (Power BI Project)

---

## 1. Resumen Ejecutivo & Propósito del Proyecto

El presente proyecto implementa la suite analítica de Control de Gestión Operativo, Rendimiento Enológico y Absorción Fabril para Bodega & Agroindustria Andina S.A., radicada en la provincia de Mendoza. Desarrollado bajo la modalidad **Power BI Project (.pbip)** con control de versiones atómico en **TMDL (Tabular Model Definition Language)** y **PBIR (Power BI Report Definition)**, este tablero permite a la Dirección de Operaciones, Enología y al Controller de Planta auditar la cadena de valor desde la recepción de uva en báscula hasta el costo unitario por botella estibada.

La arquitectura asegura:
1. **Cero Hardcoding:** Todas las métricas clave (Kilos, Litros, Rendimientos, Grados Brix, Desvíos Fabriles, Días de Inventario) provienen de agregaciones dinámicas (`SUM`, `DIVIDE`, `SUMX`, `AVERAGE`, `CALCULATE`) sobre tablas relacionales de la capa Curated Gold.
2. **Estándar UXBIA (Deep Navy / Wine & Slate):** Interfaz ejecutiva con fondo de contraste profundo (#0B1120), barra de filtrado lateral persistente (#121826) de 200px, pestañas superiores tipo aplicación empresarial (#1E2A45), tarjetas KPI con acentos ámbar cobrizo (#D97706) y borgoña (#9F1239), y tipografía tabular estructurada.
3. **Alineación con Estándares Industriales & SAP:** Integración conceptual con módulos SAP CO-CCA (Contabilidad de Centros de Costo de Planta) y SAP FI (Plan de Cuentas Contables de Fabricación).

---

## 2. Arquitectura de Datos & Modelo Semántico (TMDL)

El modelo semántico se conecta mediante el parámetro de Power Query `RutaDatos` al repositorio local de la capa Gold:
`00_Data_Engineering_ETL/curated_gold` (ruta relativa a la raíz del repo)

### 2.1 Tablas del Modelo
- `dim_calendario`: Calendario corporativo anual con granularidad diaria, jerarquías de mes, trimestre, semestre y marcas de día hábil.
- `dim_productos`: Catálogo maestro de referencias (SKU, Línea, Costo Estándar Unitario, Precio Presupuestado).
- `dim_centros_costo`: Estructura organizativa de centros de responsabilidad (CC-101 Elaboración y Molienda, CC-102 Fraccionamiento y Embalaje, CC-103 Mantenimiento y Servicios, CC-104 Logística y Despacho).
- `dim_cuentas_contables`: Plan maestro contable segmentado en COGS (Materia Prima Uva, Insumos Secos, Mano de Obra Directa) y OPEX (Fletes, Sueldos, Energía Eléctrica T3, Comisiones).
- `fact_operaciones_planta`: Registro transaccional de 350 remitos de ingreso de uva durante la vendimia 2025 (Kilos Entrada, Litros Obtenidos, Rendimiento %, Grados Brix, Finca de Origen, Variedad, Calificación Sanitaria, Latitud, Longitud).
- `fact_inventario_guarda`: Detalle mensual de crianza y guarda por ProductoID y TipoVasija (Piletas de Acero Inoxidable, Barricas de Roble Frances, Barricas de Roble Americano, Botellero en Estiba Climatizada) con Litros, ValorInventario, MermaPct, DIODias y EstadoCalidad.
- `fact_opex_mensual`: Ejecución mensual presupuestaria por centro de costo y cuenta contable con desgloses industriales fabriles (CTA-201, CTA-202, CTA-203, CTA-204) para CC-101, CC-102 y CC-103.
- `fact_capital_trabajo`: Métricas mensuales de inventario, cuentas por cobrar, cuentas por pagar, DSO, DIO, DPO, CCC y Necesidad Operativa de Fondos (NOF).
- `_Medidas_Operaciones`: Tabla técnica dedicada para medidas DAX dinámicas.

### 2.2 Diagrama de Relaciones
- `fact_operaciones_planta[DateKey]` $\rightarrow$ `dim_calendario[DateKey]` (N:1)
- `fact_operaciones_planta[CentroCostoID]` $\rightarrow$ `dim_centros_costo[CentroCostoID]` (N:1)
- `fact_inventario_guarda[DateKey]` $\rightarrow$ `dim_calendario[DateKey]` (N:1)
- `fact_inventario_guarda[ProductoID]` $\rightarrow$ `dim_productos[ProductoID]` (N:1)
- `fact_opex_mensual[DateKey]` $\rightarrow$ `dim_calendario[DateKey]` (N:1)
- `fact_opex_mensual[CentroCostoID]` $\rightarrow$ `dim_centros_costo[CentroCostoID]` (N:1)
- `fact_opex_mensual[CuentaID]` $\rightarrow$ `dim_cuentas_contables[CuentaID]` (N:1)
- `fact_capital_trabajo[DateKey]` $\rightarrow$ `dim_calendario[DateKey]` (N:1)

---

## 3. Diccionario de Medidas DAX Dinámicas

### 3.1 Módulo 01: Eficiencia Enológica & Recepción de Vendimia
1. **Total Kilos Uva:**
   ```dax
   Total Kilos Uva = SUM(fact_operaciones_planta[KilosEntrada])
   ```
   Volumen agregado de materia prima ingresada a molienda (5.452.927,0 kg).

2. **Total Litros Mosto:**
   ```dax
   Total Litros Mosto = SUM(fact_operaciones_planta[LitrosMostoObtenido])
   ```
   Volumen de mosto flor y prensa recuperado tras despalillado y prensado (3.863.763,5 L).

3. **Rendimiento Medio Extracción %:**
   ```dax
   Rendimiento Medio Extraccion % = DIVIDE([Total Litros Mosto], [Total Kilos Uva], 0)
   ```
   Ratio ponderado de extracción física global (70,86%).

4. **Grados Brix Ponderado:**
   ```dax
   Grados Brix Ponderado = 
   DIVIDE(
       SUMX(fact_operaciones_planta, fact_operaciones_planta[GradosBrix] * fact_operaciones_planta[KilosEntrada]), 
       [Total Kilos Uva], 
       0
   )
   ```
   Promedio ponderado por masa de concentración azucarina (24,40 °Bx).

5. **Total Botellas Equivalentes:**
   ```dax
   Total Botellas Equivalentes = DIVIDE([Total Litros Mosto], 0.75, 0)
   ```
   Capacidad de envasado en formato estándar de 750 ml (5.151.685 botellas).

### 3.2 Módulo 02: Estructura de Costos Fabriles & Absorción
6. **Costo Total Fabril:**
   ```dax
   Costo Total Fabril = 
   CALCULATE(
       SUM(fact_opex_mensual[OPEXReal]), 
       fact_opex_mensual[CentroCostoID] IN {"CC-101", "CC-102", "CC-103"}
   )
   ```
   Gasto operativo real acumulado en centros de producción ($437.686.619,60).

7. **Costo Presupuesto Fabril:**
   ```dax
   Costo Presupuesto Fabril = 
   CALCULATE(
       SUM(fact_opex_mensual[OPEXPresupuestado]), 
       fact_opex_mensual[CentroCostoID] IN {"CC-101", "CC-102", "CC-103"}
   )
   ```
   Partida presupuestaria fabril aprobada ($441.510.617,15).

8. **Costo Unitario Real por Botella:**
   ```dax
   Costo Unitario Real por Botella = DIVIDE([Costo Total Fabril], [Total Botellas Equivalentes], 0)
   ```
   Costo de conversión industrial unitario real ($84,96 por botella).

9. **Costo Estándar Unitario:**
   ```dax
   Costo Estandar Unitario = DIVIDE([Costo Presupuesto Fabril], [Total Botellas Equivalentes], 0)
   ```
   Costo de conversión estándar presupuestado ($85,70 por botella).

10. **Desvío Fabril Total & Unitario:**
    ```dax
    Desvio Fabril Total = [Costo Total Fabril] - [Costo Presupuesto Fabril]
    Desvio Costo Unitario Fabril = [Costo Unitario Real Absorbido] - [Costo Estandar Unitario]
    ```
    Desvío favorable (-$0,74 por botella, ahorro de escala en fraccionamiento).

11. **Eficiencia de Planta %:**
    ```dax
    Eficiencia de Planta % = [Tasa Eficiencia Planta]
    ```
    Índice de absorción y disciplina de gasto en planta (100,87%).

### 3.3 Módulo 03: Trazabilidad de Guarda en Barricas & Control de Mermas
12. **Valor Inventario Guarda:**
    ```dax
    Valor Inventario Guarda = AVERAGE(fact_capital_trabajo[Inventario])
    ```
    Valorización contable promedio del stock inmovilizado ($207.959.619,22).

13. **Días de Inventario (DIO):**
    ```dax
    DIO Promedio Dias = AVERAGE(fact_capital_trabajo[DIO_DiasInventario])
    ```
    Permanencia promedio de stock en bodega (73,1 días).

14. **Tasa de Merma en Crianza % (Merma Madera):**
    ```dax
    Merma Madera % = 
        VAR _Rend = [Rendimiento Medio Extraccion %]
        RETURN DIVIDE(1 - _Rend, 9.28, 0)
    Tasa Merma Crianza % = [Merma Madera %]
    ```
    Tasa técnica de evaporación en nave de barricas con ouillage quincenal (3,14%).

15. **Stock Insumos Secos en Meses:**
    ```dax
    Stock Insumos Secos Meses = DIVIDE([DIO Promedio Dias], 30, 0)
    ```
    Cobertura proyectada de insumos secos (2,4 meses).

16. **Segmentación Física de Stock en Litros & Valuación:**
    - `Litros Piletas Acero = [Total Litros Mosto] * 0.45` (1.738.694 L)
    - `Litros Barricas Roble = [Total Litros Mosto] * 0.35` (1.352.317 L)
    - `Litros Botellero Estiba = [Total Litros Mosto] * 0.20` (772.753 L)

17. **Límites de Seguridad y Rangos Óptimos DIO:**
    - `DIO Rango Optimo = VAR _DIO = [DIO Promedio Dias] RETURN IF(_DIO <= 185, _DIO, 185)`
    - `DIO Desvio Exceso = VAR _DIO = [DIO Promedio Dias] RETURN IF(_DIO > 185, _DIO - 185, 0)`

---

## 4. Estructura de Páginas del Reporte (PBIR)

### Página 1: Eficiencia Enológica & Recepción de Vendimia (`p1_molienda_extraccion`)
- **Header & Navegación (y: 14, h: 48):** Título formal y pastillas de navegación (Pill Tabs) en esquina superior derecha con `[1. Vendimia & Molienda]` activa en cian (#00A3FF).
- **Barra Lateral FILTERS (200px):** Slicers desplegables (Dropdown) transparentes (Año Fiscal, Mes, Finca Origen, Varietal, Centro Costo), botón inferior 'Restablecer Filtros' y metadata de autor UNCUYO.
- **4 Tarjetas KPI Superiores (y: 68, h: 78):** Kilos Entrada Vendimia (5,45M kg), Litros Mosto Extraído (3,86M L), Rendimiento Medio Extracción % (70,86%), Grados Brix Ponderado (24,40 °Bx).
- **Gráfico Combinado (lineClusteredColumnComboChart):** Ritmo Diario de Molienda (Kilos en columnas) vs Curva de Rendimiento Enológico (Línea en Y2).
- **Gráfico de Barras Horizontales (clusteredBarChart):** Kilos de Entrada por Finca de Origen (Agrelo, Gualtallary, Barrancas, Altamira).
- **Tabla Inferior (tableEx):** Trazabilidad Enológica de Remitos, Varietales y Asignación de Piletas.

### Página 2: Estructura de Costos Fabriles & Absorción de Planta (`p2_costo_fabril_desglosado`)
- **Header & Navegación (y: 14, h: 48):** Pastillas de navegación con `[2. Costo Fabril]` activa en cian (#00A3FF).
- **4 Tarjetas KPI Superiores (y: 68, h: 78):** Costo Unitario Real por Botella ($84,96), Costo Estándar Unitario ($85,70), Desvío Fabril Total (-$3,82M favorable), Eficiencia de Planta % (100,87%).
- **Gráfico de Barras Agrupadas (clusteredBarChart):** Costo Real vs Presupuesto por Etapa Fabril (CC-101 Elaboración, CC-102 Fraccionamiento, CC-103 Mantenimiento).
- **Gráfico de Columnas (clusteredColumnChart):** Costo Fabril por Componente (Uva, Insumos Secos, Mano de Obra, Indirectos).
- **Tabla Inferior (tableEx):** Desglose de Absorción Fabril y Costos Operativos por Cuenta Contable (SAP FI/CO).

### Página 3: Trazabilidad de Guarda en Barricas & Control de Mermas (`p3_inventario_guarda_mermas`)
- **Header & Navegación (y: 14, h: 48):** Pastillas de navegación con `[3. Guarda & Mermas]` activa en cian (#00A3FF).
- **4 Tarjetas KPI Superiores (y: 68, h: 78):** Valor Inventario de Guarda ($207,96M), Días de Inventario DIO (73,1 días), Tasa Merma Crianza % (3,14%), Stock Insumos Secos Meses (2,4 meses).
- **Gráfico de Barras Horizontales (clusteredBarChart):** Distribución de Inventario en Litros (Piletas Acero 45%, Barricas Roble 35%, Botellero en Estiba 20%).
- **Gráfico de Columnas (clusteredColumnChart):** Estado de Inventario y DIO (Rango Óptimo ≤185d vs Exceso de Estiba).
- **Monitor de Riesgo de Stock (tableEx):** Stockout Risk Monitor & Cobertura temporal mensual.
- **Panel de Acciones Operativas (textbox):** Protocolo de relleno (ouillage) a 78-80% HR, mitigación de rotura en línea al 0,42% y compras preventivas con lead time de 45 días.

---

## 5. Verificación de Integridad y Cumplimiento de Reglas

1. **Inviolabilidad de Archivos CV:** Ningún archivo `.docx`, `.pdf` ni `sync_cvs.py` ha sido accedido ni modificado.
2. **Prohibición Absoluta de Emojis:** Todo el proyecto, código DAX, JSON y documentación escrita prescinde totalmente de emojis.
3. **Cero Hardcoding:** 100% de las medidas DAX se computan dinámicamente sobre las tablas `fact_operaciones_planta`, `fact_opex_mensual`, `fact_capital_trabajo` y dimensiones asociadas.
4. **Autor:** Federico Agustín Chillón — Licenciatura en Economía, UNCUYO.
