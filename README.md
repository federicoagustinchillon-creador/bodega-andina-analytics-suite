# SUITE DE ANALÍTICA EMPRESARIAL & CONTROL DE GESTIÓN (POWER BI / FABRIC PBIP)
## BODEGA & AGROINDUSTRIA ANDINA S.A. (MENDOZA, ARGENTINA)

**Autor:** Federico Agustín Chillón  
**Afiliación Académica:** Facultad de Ciencias Económicas — Universidad Nacional de Cuyo (UNCUYO)  
**Estándar de Arquitectura:** Microsoft Fabric Developer Mode (`.pbip`), TMDL Semántico, PBIR Report  
**Estándar Visual:** Deep Navy Executive UXBIA (Lienzo `#0B1120`, Tarjetas `#131C31`, Acentos Borgoña `#9F1239` y Cian `#0EA5E9`)  
**Fecha de Publicación:** Septiembre 2026  

---

## 1. VISIÓN GENERAL Y OBJETIVO ESTRATÉGICO

El presente ecosistema analítico constituye una plataforma integral de **Control de Gestión, Inteligencia Comercial y Cadena de Suministro** diseñada específicamente para la industria vitivinícola y agroindustrial de exportación. 

A diferencia de los modelos monolíticos tradicionales —que concentran decenas de pestañas heterogéneas en un único archivo pesado y lento—, este portafolio adopta una **arquitectura desacoplada en 4 módulos independientes**:

```
Portfolio_Empresarial_PowerBI/
├── Ingenieria_de_Datos/          # Ingestion, Limpieza en Python, Calidad 100% y DDL/Vistas SQL
├── Control_de_Gestion/      # P&L Cascada, Centros de Costo SAP CO-CCA, Liquidez y Capital de Trabajo
├── Inteligencia_Comercial/ # Rentabilidad Multicanal, Precios vs Lista, Curva de Pareto 80/20
├── Operaciones_y_Planta/  # Eficiencia Enológica, Costos Fabriles de Absorción, Mermas y Crianza
├── tools/                            # Scripts de auditoria automatizada anti-hardcodes y verificacion
└── sync_all_suites.py                # Orquestador maestro y sincronizacion a Google Drive Master
```

Esta separación garantiza:
1. **Atención focalizada por stakeholder:** El CFO audita la suite financiera, el Director Comercial analiza márgenes por canal y el Gerente de Operaciones supervisa los rendimientos de extracción y mermas en bodega.
2. **Gobernanza y Versionado Git:** Gracias al formato **Microsoft Fabric Developer Mode (`.pbip`)**, el modelo semántico se almacena en lenguaje declarativo plano (**TMDL**) y las páginas del reporte en archivos JSON modulares (**PBIR**), permitiendo control de versiones granular, auditorías de diffs y despliegues CI/CD.
3. **Cero Hardcoding & Cuadratura Exacta:** El 100% de las métricas son calculadas dinámicamente mediante DAX sobre los datos curados. En particular, la descomposición de variaciones (*Variance Analysis*) cumple con la identidad matemática de cierre exacto ($\$0.00$ de residuo).

---

## 2. EXPLICACIÓN CONCEPTUAL: PROTOCOLO FEYNMAN EN 4 CAPAS

Para garantizar una comprensión profunda tanto por evaluadores técnicos como por directores de negocio, cada componente de la suite se desglosa en 4 niveles de abstracción:

### Nivel 1: Intuición y Sentido de Negocio
Una bodega de alta gama no gana dinero únicamente vendiendo vino; lo gana controlando tres variables críticas:
- **Efecto Precio ($EP$):** Cobrar por encima del costo inflacionario sin deteriorar la demanda.
- **Efecto Mezcla / Volumen ($EV$):** Desplazar el mix de ventas hacia botellas de mayor margen unitario (Líneas Reserva vs. Clásico o Graneles).
- **Efecto Eficiencia Operativa ($EC$):** Extraer la máxima cantidad de mosto flor sin degradar la calidad enológica y minimizar los días de inmovilización de capital en barricas y botelleros.

### Nivel 2: Arquitectura Institucional y Estructura ERP
El flujo de datos se estructura bajo el estándar de **Star Schema (Esquema en Estrella)**:
- **Tablas de Hechos (Facts):** Contienen los eventos cuantitativos del negocio transaccional:
  * `fact_ventas_reales`: Facturación granular sincronizada desde SAP SD (`VBRP/VBRK`).
  * `fact_presupuesto_ventas`: Metas mensuales y anuales acordadas por el Directorio.
  * `fact_opex_mensual`: Gastos operativos reales vs. plan por Centro de Costo (SAP CO-CCA).
  * `fact_capital_trabajo`: Saldos patrimoniales de balance (CxC, Inventarios, CxP) y ratios de rotación.
  * `fact_operaciones_planta`: Remitos de báscula de vendimia, pesajes y grados Brix.
- **Tablas de Dimensiones (Dimensions):** Proveen el contexto analítico y filtrado:
  * `dim_calendario`: Dimensión temporal estructurada con granularidad diaria y orden cronológico.
  * `dim_productos`: Maestro de SKUs, líneas enológicas y costos estándar.
  * `dim_centros_costo`: Estructura jerárquica de centros de responsabilidad operativa.
  * `dim_cuentas_contables`: Plan de cuentas corporativo estructurado por rubro de gasto.

### Nivel 3: Primeros Principios Matemáticos

#### A. Descomposición Ortogonal del Margen Bruto (Variance Analysis de 3 Factores)
El desvío total entre el Margen Bruto Real ($MB_R$) y el Presupuestado ($MB_P$) se descompone de forma exacta a nivel de cada SKU $i$:
$$\Delta MB = MB_R - MB_P = \sum_{i} \left( EV_i + EP_i + EC_i \right)$$

Donde:
1. **Efecto Volumen ($EV_i$):**
   $$EV_i = (Q_{R,i} - Q_{P,i}) \times (P_{P,i} - C_{P,i})$$
   Aísla la ganancia o pérdida atribuible estrictamente a vender más o menos unidades, valuada al margen unitario presupuestado.
2. **Efecto Precio ($EP_i$):**
   $$EP_i = Q_{R,i} \times (P_{R,i} - P_{P,i})$$
   Mide el impacto de las variaciones en las listas de precios y descuentos comerciales sobre las unidades efectivamente vendidas.
3. **Efecto Costo ($EC_i$):**
   $$EC_i = Q_{R,i} \times (C_{P,i} - C_{R,i})$$
   Captura la ganancia por ahorro o pérdida por sobrecostos fabriles unitarios.

**Propiedad de Cierre Exacto:**
$$\Delta MB - (EV + EP + EC) \equiv 0.00$$

#### B. Ciclo de Conversión de Efectivo (CCC) y Necesidad Operativa de Fondos (NOF)
$$\text{CCC} = \text{DSO} + \text{DIO} - \text{DPO}$$
$$\text{NOF} = \text{Cuentas por Cobrar} + \text{Inventarios} - \text{Cuentas por Pagar}$$
- $\text{DSO}$ (Días de Cobro): $\frac{\text{CxC}}{\text{Ventas Diarias}}$
- $\text{DIO}$ (Días de Inventario): $\frac{\text{Inventario}}{\text{Costo Diario}}$
- $\text{DPO}$ (Días de Pago): $\frac{\text{CxP}}{\text{Compras Diarias}}$

#### C. Rendimiento Enológico y Balance de Masa
$$\text{Rendimiento de Extracción (\%)} = \frac{\text{Litros de Mosto Obtenidos}}{\text{Kilos de Uva Ingresados}} \times 100$$
$$\text{Grados Brix Ponderados} = \frac{\sum (Brix_k \times Kilos_k)}{\sum Kilos_k}$$

### Nivel 4: Código Bare-Metal y Fórmulas DAX

#### Cálculo Iterativo de Variaciones en DAX:
```dax
Efecto Volumen EV = 
SUMX(
    VALUES(dim_productos[ProductoID]),
    VAR VolReal = [Volumen Real]
    VAR VolPlan = [Volumen Presupuesto]
    VAR MargenUnitPlan = [Margen Bruto Unitario Presupuesto]
    RETURN (VolReal - VolPlan) * MargenUnitPlan
)

Efecto Precio EP = 
SUMX(
    VALUES(dim_productos[ProductoID]),
    VAR VolReal = [Volumen Real]
    VAR PrecioReal = [Precio Promedio Real]
    VAR PrecioPlan = [Precio Promedio Presupuestado]
    RETURN VolReal * (PrecioReal - PrecioPlan)
)

Efecto Costo EC = 
SUMX(
    VALUES(dim_productos[ProductoID]),
    VAR VolReal = [Volumen Real]
    VAR CostoPlan = [Costo Unitario Presupuestado]
    VAR CostoReal = [Costo Unitario Real]
    RETURN VolReal * (CostoPlan - CostoReal)
)

Verificacion Desvio Cuadrado = 
ROUND([Desvio Margen Bruto Total] - ([Efecto Volumen EV] + [Efecto Precio EP] + [Efecto Costo EC]), 2)
```

---

## 3. DETALLE DE LAS SUITES INDEPENDIENTES

### Suite 01: Financial Controller & FP&A (`Control_de_Gestion.pbip`)
- **Página 1: P&L Ejecutivo & Descomposición de Desvíos:**
  * 4 KPIs: Ingresos Netos ($1,474.5M), Margen Bruto ($768.6M / 52.13%), EBITDA ($312.8M), Ciclo de Conversión de Efectivo (62.9 días).
  * Waterfall Chart interactivo de Variance Analysis que reconcilia Plan $\rightarrow EV \rightarrow EP \rightarrow EC \rightarrow$ Real con residuo cero.
  * Matriz por línea enológica con barras proporcionales.
- **Página 2: Control Presupuestario OPEX (SAP CO-CCA):**
  * Comparativo por Centro de Costo (Molienda CC-101, Fraccionamiento CC-102, Cava CC-104, etc.).
  * Alertas presupuestarias con semáforos de tolerancia ($Verde \le 0\%$, $Amarillo \le 5\%$, $Rojo > 5\%$).
  * Apertura por Plan de Cuentas SAP FI (Fletes, Sueldos, Suministros, Servicios).
- **Página 3: Liquidez, NOF y Flujo de Fondos:**
  * Indicadores de capital de trabajo: DSO (25.7d), DIO (73.1d), DPO (35.9d), CCC (62.9d), NOF ($241.6M).
  * Curvas de rotación mensual y estructura patrimonial de NOF.
  * Panel de síntesis ejecutiva estructurado bajo el método Pirámide de Minto.

### Suite 02: Commercial & Sales Intelligence (`Inteligencia_Comercial.pbip`)
- **Página 1: Inteligencia Multicanal:**
  * Facturación y cumplimiento por canal: Canal Horeca, Supermercados, Distribuidor Mayorista, Exportación Directa.
  * Gráfico de dispersión cuadrante: Volumen Vendido ($X$) vs. Precio Promedio Real ($Y$) con burbujas ponderadas por margen.
- **Página 2: Dinámica de Precios Reales vs. Lista:**
  * Auditoría de dispersión de precios efectivos frente al presupuesto.
  * Control de bonificaciones y descuentos comerciales concedidos a grandes superficies.
- **Página 3: Análisis de Portafolio & Curva de Pareto 80/20:**
  * Clasificación dinámica ABC de SKUs.
  * Los SKUs Clase A (Bag in Box 3L, Cabernet Franc Reserva, Malbec Reserva) concentran el 70.63% de la facturación con un margen promedio del 52.36%.
  * Panel de recomendaciones estratégicas de blindaje de stock y rentabilidad.

### Suite 03: Operations & Supply Chain Plant (`Operaciones_y_Planta.pbip`)
- **Página 1: Eficiencia Enológica & Recepción de Vendimia:**
  * Balance de masa: 5,452,927 kg de uva procesada $\rightarrow$ 3,863,764 L de mosto (Rendimiento medio 70.86%, Grados Brix 24.40°Bx).
  * Rendimiento por finca de origen (Finca Agrelo, Barrancas, Gualtallary, Altamira).
  * Auditoría de 350 remitos de báscula con trazabilidad lote a lote.
- **Página 2: Estructura de Costos Fabriles & Absorción:**
  * Costo unitario real ($84.96/botella) vs. estándar ($85.70/botella) $\rightarrow$ Ahorro favorable de -$0.74/botella (Eficiencia 100.87%).
  * Absorción fabril por centro de costo y cuenta de planta (Mano de obra, Energía T3, Fletes).
- **Página 3: Guarda en Barricas, Crianza & Control de Mermas:**
  * Valor de inventario en guarda ($207.96M, 73.1 días de DIO).
  * Segmentación física: Piletas de acero inoxidable (45%), Barricas de roble francés/americano (35%) y Estiba en cava (20%).
  * Monitoreo de tasa de merma por evaporación (*ouillage*) y rotura en línea de envasado.

---

## 4. GUÍA DE APERTURA Y DESPLIEGUE EN POWER BI DESKTOP

1. **Requisitos:** Microsoft Power BI Desktop (edición 2024 o superior) con la opción de vista previa **Power BI Project (`.pbip`)** habilitada en `Opciones -> Características de versión preliminar`.
2. **Apertura de Proyectos:**
   - Para abrir la suite financiera: doble clic en `Control_de_Gestion/Control_de_Gestion.pbip`.
   - Para abrir la suite comercial: doble clic en `Inteligencia_Comercial/Inteligencia_Comercial.pbip`.
   - Para abrir la suite de planta: doble clic en `Operaciones_y_Planta/Operaciones_y_Planta.pbip`.
3. **Parámetro de Datos Portable (`RutaDatos`):**
   Todos los modelos leen los datos limpios mediante el parámetro `RutaDatos` configurado en `expressions.tmdl`. Si se reubica la carpeta, basta con ir a `Inicio -> Transformar datos -> Editar parámetros` e ingresar la nueva ruta a `curated_gold`.

---

## 5. REPORTE DE AUDITORÍA Y CERTIFICACIÓN DE CALIDAD

La suite ha sido auditada exhaustivamente mediante el script automatizado `tools/audit_powerbi_suite.py`:
- **Archivos TMDL validados:** 24 archivos de modelos relacionales y medidas.
- **Archivos JSON / PBIP / PBIR verificados:** 175 archivos de configuración y contenedores visuales.
- **Medidas DAX escaneadas:** 108 medidas.
- **Violaciones de Hardcoding detectadas:** 0 (Cero números mágicos; toda métrica es calculada).
- **Errores de sintaxis de esquemas:** 0.
- **Auditoría de Emojis:** 0 emojis en todo el código y metadatos.
- **Integridad de Currículums:** 0 modificaciones a archivos de CV.

---
*Facultad de Ciencias Económicas — Universidad Nacional de Cuyo (UNCUYO)*  
*Mendoza, Argentina — 2026*
