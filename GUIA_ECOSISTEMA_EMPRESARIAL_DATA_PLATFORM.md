# ECOSISTEMA EMPRESARIAL DE ANALÍTICA, GOBERNANZA DE DATOS & CONTROL DE GESTIÓN
## PLATAFORMA INTEGRAL DE BUSINESS INTELLIGENCE — BODEGA & AGROINDUSTRIA ANDINA S.A.

**Autor & Arquitecto:** Federico Agustín Chillón  
**Afiliación Académica:** Facultad de Ciencias Económicas — Universidad Nacional de Cuyo (UNCUYO)  
**Formato Tecnológico:** Microsoft Fabric PBIP (Power BI Project), TMDL Semántico, PBIR Report Layer  
**Stack de Ingeniería:** Python 3.12, Pandas, DuckDB, PostgreSQL DDL/Views, DAX Tabular Engine  
**Estándar de Diseño:** Deep Navy Executive UXBIA (Lienzo `#0B1120`, Tarjetas `#131C31`, Acentos Borgoña `#9F1239` y Cian `#00A3FF`)  
**Fecha de Certificación:** Septiembre 2026 · **Estado:** Auditado al 100% (Zero Missing References)  

---

## 1. RESUMEN EJECUTIVO & ARQUITECTURA GENERAL DEL SISTEMA

La presente plataforma representa una solución integral de analítica avanzada, control de gestión e inteligencia de negocios desarrollada específicamente para la industria vitivinícola y agroindustrial exportadora.

Frente a los reportes convencionales monolíticos —que sufren de rigidez, lentitud y falta de gobierno de datos—, esta suite implementa una **arquitectura desacoplada en 4 niveles operativos**:

```
                                    ARQUITECTURA DE FLUJO DE DATOS END-TO-END
                                    
   [ FUENTES CRUDAS ERP / PLANTA ]               [ CAPA 00: DATA ENGINEERING ]             [ CAPA SEMÁNTICA TMDL ]              [ CAPA VISUAL PBIR (9 PÁGINAS) ]
   
   +-------------------------------+             +---------------------------+              +-----------------------+            +----------------------------------+
   | - raw_sap_vbrk_vbrp_ventas    |             |  etl_pipeline_cleaner.py  |              |  Modelos Semánticos   |            |  02_Control_de_Gestion     |
   | - raw_presupuesto_horizontal  | ----------> |  - Stripping & Mayúsculas | -----------> |  - Relaciones 1:*     | ---------> |  p1. P&L & Variance Cascada      |
   | - raw_planta_molienda_remitos |             |  - Parseo Fechas 8 Formatos|             |  - 136 Medidas DAX    |            |  p2. OPEX por Centro de Costo    |
   | - raw_maestro_centros_costo   |             |  - Unpivot Dinámico Plan  |              |  - Cero Hardcoding    |            |  p3. Capital Trabajo & Liquidez  |
   | - raw_maestro_productos       |             |  - Integridad Referencial |              |  - Parámetro RutaDatos|            +----------------------------------+
   | - raw_balance_capital_trabajo |             |  - data_quality_report    |              +-----------------------+            |  02_Commercial_Sales_Intell.     |
   +-------------------------------+             +---------------------------+                                                   |  p1. Desempeño Multicanal        |
                                                               |                                                                 |  p2. Dinámica de Precios Real    |
                                                               v                                                                 |  p3. Portafolio ABC & Pareto     |
                                                 +---------------------------+                                                   +----------------------------------+
                                                 |   curated_gold/ (CSVs)    |                                                   |  04_Operaciones_y_Planta |
                                                 |   sql/ (DDL & Vistas)     |                                                   |  p1. Vendimia & Extracción       |
                                                 +---------------------------+                                                   |  p2. Costos Fabriles Absorción   |
                                                                                                                                 |  p3. Guarda, Mermas & Crianza    |
                                                                                                                                 +----------------------------------+
```

### Principios Rectores del Proyecto:
1. **Control de Gestión con Rigor Académico:** Aplicación de identidades matemáticas formales (Descomposición de Desvíos de 4 factores de Horváth & Partners / IBCS, Rotaciones de Capital de Trabajo y Balance de Masa Enológico).
2. **Cero Hardcoding & Cuadratura Exacta:** El 100% de las cifras son calculadas dinámicamente en memoria mediante DAX. Se garantiza cuadratura contable estricta con residuo idénticamente nulo ($0.00).
3. **Developer Mode Nativo (PBIP):** Modelos definidos en **TMDL** y reportes en **PBIR**, permitiendo versionado atómico en Git, revisiones de código por pares (*pull requests*) y despliegues reproducibles.
4. **Ergonomía Visual Ejecutiva (Deep Navy UXBIA):** Jerarquía de información calibrada para directores generales y comités ejecutivos, eliminando la sobrecarga cognitiva mediante paletas de alto contraste sobre fondo oscuro institucional (#0B1120).

---

## 2. CAPA 00: INGENIERÍA DE DATOS, CURACIÓN & AUDITORÍA DE CALIDAD

### 2.1 Desafíos de Datos del Negocio Real
En entornos productivos, los sistemas transaccionales nunca entregan datos limpios. Esta suite reproduce de forma realista las siguientes inconsistencias comunes:
- **SAP SD/MM:** Códigos de materiales con capitalización inconsistente (`mal-res-750` vs `MAL-RES-750`), espacios espurios, y formatos de fecha combinados (`YYYY-MM-DD`, `DD/MM/YYYY`, `YYYY/MM/DD`, `YYYYMMDD`).
- **Presupuestos Horizontales:** Planillas comerciales donde los 12 meses están dispuestos como columnas (`Ene_Vol`, `Feb_Vol`, ..., `Dic_Ing`), impidiendo su agregación columnar directa.
- **Báscula y Planta:** Remitos de vendimia con nombres de terroir variantes (`Agrelo`, `Finca Agrelo`, `agrelo`) y registros manuales con posibles valores nulos.
- **Integridad Referencial Rota:** Transacciones con códigos de productos inexistentes en el maestro.

### 2.2 Pipeline de Extracción y Limpieza (`etl_pipeline_cleaner.py`)
El motor de ingeniería de datos ejecuta de forma determinista:
1. **Normalización Tipográfica:** Eliminación de espacios en blanco (`strip`), colapso de espacios múltiples y conversión a mayúsculas de todas las claves primarias y foráneas.
2. **Algoritmo Robusto de Parseo Temporal:** Motor heurístico que evalúa secuencialmente 8 patrones de fecha, normaliza a ISO 8601 (`YYYY-MM-DD`) y genera la clave subrogada entera `DateKey` (`YYYYMMDD`).
3. **Unpivot Matricial de Presupuesto:** Transformación columnar (*melt*) que colapsa las 24 columnas mensuales en una estructura tidy relacional (`DateKey`, `ProductoID`, `CentroCostoID`, `VolumenPresupuestado`, `IngresosPresupuestados`, `CostoPresupuestado`, `MargenBrutoPresupuestado`), calculando márgenes unitarios presupuestados.
4. **Validación de Integridad Referencial:** Comprobación de claves foráneas entre cada tabla de hechos y sus dimensiones asociadas. El pipeline detecta, resuelve y audita cualquier registro huérfano.
5. **Clasificación ABC Determinista:** Enriquecimiento de `Productos` con la columna `CategoriaABC` según la jerarquía de cartera (`Alta Gama` y `Granel / Masivo` -> Clase A; `Espumantes` -> Clase B; `Entrada / Volumen` -> Clase C).

### 2.3 Auditoría Automatizada (`data_quality_report.json`)
Cada corrida del pipeline genera un certificado JSON auditable:
- **Tablas Procesadas:** 9 tablas (4 dimensiones, 5 hechos).
- **Registros Auditados:** >2.500 transacciones.
- **Inconsistencias Corregidas:** 100% saneadas.
- **Claves Huérfanas Residuales:** 0.
- **Tasa de Validez Global:** **100.00%**.

---

## 3. MODELO SEMÁNTICO (STAR SCHEMA & TMDL)

El modelo de datos se estructura bajo el estándar de **Kimball (Star Schema)** con relaciones de cardinalidad $1:N$ con dirección de filtro unidireccional, garantizando un rendimiento óptimo en el motor VertiPaq.

```
                                  DIAGRAMA RELACIONAL STAR SCHEMA
                                  
                                    +-----------------------+
                                    |    Calendario     |
                                    |-----------------------|
                                    | PK: DateKey           |
                                    +-----------------------+
                                           |     |     |
                 +-------------------------+     |     +-------------------------+
                 |                               |                               |
                 v                               v                               v
    +-----------------------+        +-----------------------+       +-----------------------+
    |   Ventas  |        |  GastosOperativos    |       | fact_operaciones_plant|
    |-----------------------|        |-----------------------|       |-----------------------|
    | FK: DateKey           |        | FK: DateKey           |       | FK: DateKey           |
    | FK: ProductoID        |        | FK: CentroCostoID     |       | FK: CentroCostoID     |
    +-----------------------+        | FK: CuentaID          |       +-----------------------+
         |                           +-----------------------+                    |
         |                                       |                                |
         v                                       v                                v
    +-----------------------+        +-----------------------+       +-----------------------+
    |     Productos     |        |   CentrosCosto   |       | PlanCuentas |
    |-----------------------|        |-----------------------|       |-----------------------|
    | PK: ProductoID        |        | PK: CentroCostoID     |       | PK: CuentaID          |
    | SKU, Descripcion,     |        | Nombre, Area,         |       | Nombre, Naturaleza,   |
    | Linea, CategoriaABC   |        | Responsable           |       | Rubro                 |
    +-----------------------+        +-----------------------+       +-----------------------+
```

### Portabilidad Absoluta (`RutaDatos`)
Todos los modelos semánticos consumen la capa Gold a través del parámetro de Power Query `RutaDatos`:
```powerquery
RutaDatos = "c:/Users/fedea/Downloads/cv/Portfolio_Empresarial_PowerBI/01_Limpieza_de_Datos/curated_gold" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]
```
Esto permite clonar el repositorio en cualquier servidor, estación de trabajo o entorno cloud cambiando únicamente un parámetro global sin reescribir consultas.

---

## 4. DICCIONARIO DE MEDIDAS DAX & PRIMEROS PRINCIPIOS ECONÓMICOS

### 4.1 Suite 01: Financial Controller & FP&A (`_Medidas_Controller`)

#### A. Descomposición Ortogonal del Margen Bruto (Variance Analysis)
El desvío global de margen bruto ($\Delta MB = MB_{Real} - MB_{Plan}$) se descompone de forma exacta a nivel de producto $i$:
$$\Delta MB = \sum_i (EV_i + EP_i + EC_i)$$

1. **Efecto Volumen ($EV$):**
   $$EV_i = (Q_{Real,i} - Q_{Plan,i}) 	imes (P_{Plan,i} - C_{Plan,i})$$
   Aísla la ganancia o pérdida atribuible exclusivamente a la variación en la cantidad de cajas vendidas, valuada al margen unitario presupuestado.
   ```dax
   Efecto Volumen EV = 
   SUMX(
       VALUES(Productos[ProductoID]),
       VAR VolReal = [Volumen Real]
       VAR VolPlan = [Volumen Presupuesto]
       VAR MargenUnitPlan = [Margen Bruto Unitario Presupuesto]
       RETURN (VolReal - VolPlan) * MargenUnitPlan
   )
   ```

2. **Efecto Precio ($EP$):**
   $$EP_i = Q_{Real,i} 	imes (P_{Real,i} - P_{Plan,i})$$
   Cuantifica el impacto de vender por encima o por debajo del precio de lista presupuestado sobre el volumen efectivamente colocado.
   ```dax
   Efecto Precio EP = 
   SUMX(
       VALUES(Productos[ProductoID]),
       VAR VolReal = [Volumen Real]
       VAR PReal = [Precio Promedio Real]
       VAR PPlan = [Precio Promedio Presupuesto]
       RETURN VolReal * (PReal - PPlan)
   )
   ```

3. **Efecto Costo ($EC$):**
   $$EC_i = Q_{Real,i} 	imes (C_{Plan,i} - C_{Real,i})$$
   Evalúa el ahorro o sobrecosto fabril unitario respecto al estándar de producción.
   ```dax
   Efecto Costo EC = 
   SUMX(
       VALUES(Productos[ProductoID]),
       VAR VolReal = [Volumen Real]
       VAR CPlan = [Costo Unitario Presupuesto]
       VAR CReal = [Costo Unitario Real]
       RETURN VolReal * (CPlan - CReal)
   )
   ```

4. **Identidad de Cierre Exacto (Cuadratura Contable):**
   ```dax
   Verificacion Cuadratura Desvios = 
   ABS([Desvio Margen Bruto $] - ([Efecto Volumen EV] + [Efecto Precio EP] + [Efecto Costo EC]))
   ```
   **Resultado:** $\$0.00$ de residuo en cualquier nivel de filtro de tiempo, producto o canal.

#### B. Capital de Trabajo, Ciclo de Conversión de Efectivo & NOF
1. **Ciclo de Conversión de Efectivo ($CCC$):**
   $$CCC = DSO + DIO - DPO$$
   - $DSO$ (Days Sales Outstanding): Días medios de cobranza a clientes.
   - $DIO$ (Days Inventory Outstanding): Días de permanencia de inventario en bodega y estiba.
   - $DPO$ (Days Payables Outstanding): Días medios de crédito comercial otorgado por proveedores.
2. **Necesidad Operativa de Fondos ($NOF$):**
   $$NOF = 	ext{Cuentas por Cobrar} + 	ext{Inventarios} - 	ext{Cuentas por Pagar}$$
   Mide el capital líquido que la empresa debe inmovilizar para sostener sus operaciones corrientes sin financiamiento bancario de corto plazo.

---

### 4.2 Suite 02: Commercial Sales Intelligence (`_Medidas_Comercial`)

1. **Cumplimiento de Cuota Comercial (%):**
   $$	ext{Cumplimiento} = rac{	ext{Ingresos Reales}}{	ext{Ingresos Presupuestados}} 	imes 100$$
2. **Descuento Comercial Concedido (%):**
   $$	ext{Descuento Medio} = rac{	ext{Precio Lista Plan} - 	ext{Precio Real Ponderado}}{	ext{Precio Lista Plan}} 	imes 100$$
3. **Curva de Lorenz y Concentración Acumulada de Ventas (%):**
   Calcula la participación porcentual acumulada de ventas ordenando los productos de forma descendente por facturación para graficar la curva de Pareto 80/20.
4. **Clasificación Dinámica ABC:**
   Agrupación analítica de SKUs para priorización comercial y política de existencias en almacén central.

---

### 4.3 Suite 03: Operations, Supply Chain & Plant (`_Medidas_Operaciones`)

1. **Rendimiento de Extracción Enológica (%):**
   $$	ext{Rendimiento} = rac{	ext{Litros de Mosto Obtenidos}}{	ext{Kilos de Uva Ingresados en Báscula}} 	imes 100$$
   Evalúa la eficiencia física del prensado por finca de origen y variedad de uva (Rango benchmark industria: 68% - 74%).
2. **Maduración Azucarina Ponderada (°Brix):**
   $$	ext{Brix Ponderado} = rac{\sum (	ext{Brix}_k 	imes 	ext{Kilos}_k)}{\sum 	ext{Kilos}_k}$$
   Monitorea el grado alcohólico potencial de la vendimia recibida.
3. **Tasa de Merma en Crianza de Roble (Ouillage %):**
   $$	ext{Merma Madera} = rac{	ext{Pérdida por Evaporación}}{	ext{Volumen Inicial en Barricas}} 	imes 100$$
   Monitoreo contra el umbral crítico de tolerancia agronómica (límite directivo: 3.5% anual).
4. **Absorción de Costo Fabril Real vs. Estándar:**
   Liquidación analítica de órdenes fabriles en Elaboración (CC-101), Fraccionamiento (CC-102) y Mantenimiento (CC-103) para determinar la variación fabril unitaria por botella.

---

## 5. ESTÁNDAR VISUAL & EXPERIENCIA DE USUARIO (DEEP NAVY UXBIA)

Los reportes fueron rediseñados y calibrados bajo el estándar **Deep Navy Executive UXBIA**, inspirado en las interfaces de terminales financieras institucionales (Bloomberg, Linear y Vercel Design):

| Componente | Posicionamiento | Especificación Visual | Función de Negocio |
| :--- | :--- | :--- | :--- |
| **Canvas Background** | `1280 x 720` | `#0B1120` (Navy Oscuro) | Lienzo oscuro antirreflejo, ideal para pantallas de alta resolución y presentaciones a Directorio. |
| **Sidebar Lateral** | `x:0, y:0, w:200, h:720` | `#0D1424`, borde `1px #1E293B` | Contenedor persistente con selectores dropdown, botón interactivo de reseteo y metadata institucional. |
| **Top Header Bar** | `x:212, y:12, w:1056, h:48` | `#0D1424`, borde `1px #1E293B` | Título formal, subtítulo analítico y pestañas de navegación directa tipo pastilla (`[● 1] [○ 2] [○ 3]`). |
| **Fila KPI Cards** | `y:66, h:88` | `#131C31`, radio `8px`, texto `20pt #F8FAFC` | 4 tarjetas horizontales (255px de ancho) con callout bold, formato en Millones ($ M) y título superior `#94A3B8`. |
| **Cuadrícula Superior** | `y:162, h:255` | Dos visuales de `522px` (`x:212` y `x:746`) | Gráficos analíticos principales (Cascadas Waterfall, Barras Horizontales, Series Multilínea). |
| **Cuadrícula Inferior** | `y:427, h:275` | Dos visuales de `522px` (`x:212` y `x:746`) | Visuales de soporte detallado (Evolución temporal, distribución ABC, matrices con totales). |

### Cero Fugas de Fondo Blanco
Se garantiza la ausencia total de pantallas o parches blancos mediante triple redundancia:
1. **Tema Semántico (`Deep_Navy_UXBIA_Theme.json`):** Clases `*`, `page`, `card`, `tableEx` y `pivotTable` configuradas con color de fondo sólido `#0B1120` y `#131C31`.
2. **Definición de Página (`page.json`):** Objetos `background` y `outspace` con propiedad `"show": true` y `"transparency": 0D`.
3. **Contenedores de Visuales (`visual.json`):** Cada contenedor visual posee su propiedad de fondo activada con `#131C31` y borde `#1E293B`.

---

## 6. DICCIONARIO COMPLETO DE DATOS (DATA DICTIONARY)

### 6.1 Tabla `Calendario` (Dimensión Temporal)
- `DateKey` (`INTEGER`, PK): Clave temporal entera formato `YYYYMMDD`.
- `Fecha` (`DATE`, UNIQUE): Fecha en formato calendario gregoriano `YYYY-MM-DD`.
- `Anio` (`INTEGER`): Año fiscal (2025).
- `MesNumero` (`INTEGER`): Número de mes del 1 al 12.
- `MesNombre` (`VARCHAR(20)`): Nombre completo en español (Enero a Diciembre).
- `Trimestre` (`VARCHAR(5)`): Trimestre calendario (T1, T2, T3, T4).
- `Semestre` (`VARCHAR(5)`): Semestre calendario (S1, S2).
- `EsFinDeSemana` (`INTEGER`): Indicador binario (1: Sábado/Domingo, 0: Día Hábil).

### 6.2 Tabla `Productos` (Catálogo de Artículos & SKUs)
- `ProductoID` (`VARCHAR(20)`, PK): Identificador único interno del producto (PRD-01 a PRD-05).
- `SKU` (`VARCHAR(50)`, UNIQUE): Código comercial del SKU (ej. `MAL-RES-750`).
- `Descripcion` (`VARCHAR(100)`): Nombre comercial de la etiqueta (ej. `Malbec Reserva 750ml`).
- `Linea` (`VARCHAR(50)`): Cartera enológica (`Alta Gama`, `Granel / Masivo`, `Espumantes`, `Entrada / Volumen`).
- `CostoEstandarUnit` (`NUMERIC(14,2)`): Costo fabril unitario presupuestado por botella en ARS ($).
- `PrecioPresupuestadoUnit` (`NUMERIC(14,2)`): Precio de lista oficial presupuestado por botella en ARS ($).
- `CategoriaABC` (`VARCHAR(20)`): Segmentación estratégica de cartera (`Clase A`, `Clase B`, `Clase C`).

### 6.3 Tabla `CentrosCosto` (Centros de Responsabilidad)
- `CentroCostoID` (`VARCHAR(20)`, PK): Código del centro de costo SAP CO-CCA (`CC-101` a `CC-105`).
- `NombreCentroCosto` (`VARCHAR(100)`): Denominación operativa (Molienda, Fraccionamiento, Mantenimiento, Logística, Administración).
- `Area` (`VARCHAR(50)`): Macro-área de la empresa (`Operaciones Planta`, `Logística y Distribución`, `Administración y Finanzas`).
- `Responsable` (`VARCHAR(100)`): Gerente o jefe de área a cargo del centro de imputación.

### 6.4 Tabla `PlanCuentas` (Plan de Cuentas FI)
- `CuentaID` (`VARCHAR(20)`, PK): Código de imputación contable (ej. `CTA-501`).
- `NombreCuenta` (`VARCHAR(120)`): Descripción contable (Materia Prima Uva, Mano de Obra, Insumos Secos, Fletes, etc.).
- `Naturaleza` (`VARCHAR(30)`): `Ingresos`, `Costos`, `Gastos Operativos`.
- `Rubro` (`VARCHAR(30)`): Agrupación ejecutiva (`Revenue`, `COGS`, `OPEX`).

### 6.5 Tabla `Ventas` (Facturación Transaccional SAP SD)
- `TransaccionID` (`VARCHAR(30)`, PK): Número de factura fiscal (`VBRK/VBRP`).
- `DateKey` (`INTEGER`, FK): Enlace a `Calendario`.
- `ProductoID` (`VARCHAR(20)`, FK): Enlace a `Productos`.
- `CanalVenta` (`VARCHAR(50)`): Canal comercial (`Exportacion Directa`, `Supermercados`, `Distribuidor Mayorista`, `Horeca`).
- `VolumenReal` (`INTEGER`): Cajas físicas facturadas.
- `IngresosReales` (`NUMERIC(16,2)`): Facturación neta total en ARS ($).
- `CostoReal` (`NUMERIC(16,2)`): Costo mercaderías vendidas real total en ARS ($).
- `MargenBrutoReal` (`NUMERIC(16,2)`): Ingresos Reales - Costo Real en ARS ($).

### 6.6 Tabla `PresupuestoVentas` (Metas Comerciales Unpivoteadas)
- `DateKey` (`INTEGER`, FK): Clave mensual presupuestada.
- `ProductoID` (`VARCHAR(20)`, FK): Clave de SKU presupuestado.
- `CentroCostoID` (`VARCHAR(20)`, FK): Centro de costo comercial imputado.
- `VolumenPresupuestado` (`INTEGER`): Meta física de venta en cajas.
- `IngresosPresupuestados` (`NUMERIC(16,2)`): Facturación presupuestada en ARS ($).
- `CostoPresupuestado` (`NUMERIC(16,2)`): Costo presupuestado total en ARS ($).
- `MargenBrutoPresupuestado` (`NUMERIC(16,2)`): Margen objetivo en ARS ($).

### 6.7 Tabla `GastosOperativos` (Ejecución Presupuestaria de Gasto)
- `DateKey` (`INTEGER`, FK): Clave mensual de imputación contable.
- `CentroCostoID` (`VARCHAR(20)`, FK): Centro de imputación de gasto.
- `CuentaID` (`VARCHAR(20)`, FK): Cuenta contable de gasto.
- `GastoReal` (`NUMERIC(16,2)`): Importe ejecutado real en ARS ($).
- `GastoPresupuesto` (`NUMERIC(16,2)`): Techo de gasto presupuestado en ARS ($).
- `DesvioMonto` (`NUMERIC(16,2)`): Gasto Real - Gasto Presupuesto en ARS ($).
- `DesvioPorcentual` (`NUMERIC(8,4)`): Ratio de desvío presupuestario.

### 6.8 Tabla `CapitalTrabajo` (Posición Patrimonial Operativa)
- `DateKey` (`INTEGER`, FK): Clave mensual de corte de balance operativo.
- `AnioMes` (`VARCHAR(10)`): Etiqueta cronológica (`2025-01` a `2025-12`).
- `CuentasPorCobrar` (`NUMERIC(16,2)`): Saldo de créditos por ventas a clientes.
- `Inventarios` (`NUMERIC(16,2)`): Valuación total de existencias (materias primas, graneles y producto terminado).
- `CuentasPorPagar` (`NUMERIC(16,2)`): Saldo de deudas comerciales con proveedores.
- `NOF` (`NUMERIC(16,2)`): Necesidad Operativa de Fondos ($CxC + Stock - CxP$).
- `DSO` (`NUMERIC(8,2)`): Días medios de cobro.
- `DIO` (`NUMERIC(8,2)`): Días medios de rotación de inventarios.
- `DPO` (`NUMERIC(8,2)`): Días medios de pago a proveedores.
- `CCC` (`NUMERIC(8,2)`): Ciclo neto de caja en días ($DSO + DIO - DPO$).

### 6.9 Tabla `ProduccionPlanta` (Recepción de Vendimia & Molienda)
- `RemitoID` (`VARCHAR(30)`, PK): Número de remito de báscula de ingreso de uva.
- `DateKey` (`INTEGER`, FK): Fecha de pesaje en báscula de bodega.
- `CentroCostoID` (`VARCHAR(20)`, FK): Centro de imputación de planta (`CC-101`).
- `FincaOrigen` (`VARCHAR(100)`): Terroir de procedencia (`Finca Agrelo`, `Finca Gualtallary`, `Finca Barrancas`, `Finca Altamira`).
- `VariedadUva` (`VARCHAR(50)`): Variedad enológica (`Malbec`, `Cabernet Franc`, `Syrah`, `Bonarda`, `Chardonnay`).
- `KilosEntrada` (`NUMERIC(14,2)`): Peso neto de uva ingresada en tolva de molienda (kg).
- `LitrosMostoObtenido` (`NUMERIC(14,2)`): Volumen de mosto extraído tras prensado (L).
- `RendimientoExtraccion` (`NUMERIC(8,4)`): Relación Litros / Kilos (Benchmark: ~0.70).
- `GradosBrix` (`NUMERIC(6,2)`): Medición refractométrica de maduración azucarina (°Bx).
- `EstadoSanitario` (`VARCHAR(30)`): Calificación fitosanitaria de la uva (`Excelente`, `Optimo`, `Bueno`).

---

## 7. PROTOCOLO DE AUDITORÍA, REPRODUCIBILIDAD & VERIFICACIÓN

Para verificar la integridad absoluta del sistema en cualquier entorno:

1. **Auditoría Automatizada de Esquemas y Medidas:**
   ```bash
   python Portfolio_Empresarial_PowerBI/tools/audit_powerbi_suite.py
   ```
   *Salida esperada:* 24 archivos TMDL escaneados, 187 archivos PBIR validados, 136 medidas DAX sin hardcoding, 0 errores sintácticos.

2. **Validación Exhaustiva de Referencias Semánticas:**
   ```bash
   python scratch/validate_references.py
   ```
   *Salida esperada:* `PASS: 100% of visual references exist in semantic model!` para los tres proyectos (189 proyecciones validadas).

3. **Ejecución del Pipeline de Ingeniería:**
   ```bash
   python Portfolio_Empresarial_PowerBI/01_Limpieza_de_Datos/etl_pipeline_cleaner.py
   ```
   *Salida esperada:* Ejecución en <0.5s con generación de `curated_gold/` y `data_quality_report.json` con 100% de validez.

4. **Sincronización Automática con Google Drive:**
   ```bash
   python scratch/sync_powerbi_to_gdrive.py
   ```
   Sincroniza y verifica los 9 archivos críticos en ambas rutas de Google Drive (`Proyecto Empresarial/Portfolio_Empresarial_PowerBI` y `Portfolio_Empresarial_PowerBI`).

---

## 8. IDENTIDAD INSTITUCIONAL & CRÉDITOS

- **Autor:** Federico Agustín Chillón
- **Institución:** Facultad de Ciencias Económicas — Universidad Nacional de Cuyo (UNCUYO)
- **Mendoza, Argentina — 2026**
