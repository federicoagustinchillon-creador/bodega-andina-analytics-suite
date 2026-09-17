# MATRIZ ESTRATÉGICA DE STAKEHOLDERS, PROBLEMAS DE NEGOCIO Y OBJETIVOS DE DECISIÓN
## Suite Empresarial Power BI — Bodega & Agroindustria Andina S.A.
**Autor Institucional:** Federico Agustín Chillón  
**Afiliación Académica:** Facultad de Ciencias Económicas — Universidad Nacional de Cuyo (UNCUYO)  
**Fecha de Publicación:** Septiembre 2026  
**Ecosistema:** Fabric Developer Mode (TMDL / PBIR / Git Integration)

---

## 1. Declaración de Misión y Enfoque Directivo

La **Suite Empresarial Power BI** no constituye un mero repositorio de paneles visuales descriptivos, sino un **Sistema Integrado de Decisión Ejecutiva y Mitigación de Riesgos** diseñado para alinear las operaciones agronómicas, fabriles y comerciales con la estrategia financiera de largo plazo de **Bodega & Agroindustria Andina S.A.**.

Cada módulo ha sido construido para responder a preguntas estratégicas concretas de directores de área, erradicando la intuición desinformada y sustituyéndola por **analítica prescriptiva, semáforos de tolerancia basados en costos de oportunidad y modelado cuantitativo avanzado**.

---

## 2. Matriz Ejecutiva por Módulo

| Módulo / PBIP | Stakeholder Principal | Problema Crítico de Negocio | Objetivo Cuantificable (KPI / Target) | Palanca de Decisión / Acción Prescriptiva |
| :--- | :--- | :--- | :--- | :--- |
| **02_Control_de_Gestion.pbip** | **CFO / Financial Controller** | Volatilidad del ciclo de caja (CCC > 85d) y fondos ociosos sin rendimiento en contexto de alta tasa (TNA 42%). | • Mantener $CCC \le 65$ días.<br>• Cuadratura de P&L Variance $= \$0.00$.<br>• Cero fondos ociosos sobre banda $h$. | **Modelo Miller-Orr:** Suscripción automática de LECAPs/FCI Money Market ante excesos de caja sobre límite $h$, y desinversión programada si toca piso $L$ (\$8.5M). |
| **03_Inteligencia_Comercial.pbip** | **CCO / Director Comercial** | Presión de cadenas de retail por descuentos excesivos sin elasticidad y descalce estacional de cuotas. | • Blindar nivel de servicio en SKUs A $\ge 98\%$.<br>• Cumplimiento de cuota mensual $\ge 95\%$.<br>• Margen bruto comercial $> 48\%$. | **Pricing por Elasticidad Causal:** Aplicar aumentos $+5\%$ a $+8\%$ sobre IPC en segmentos inelásticos (Gran Reserva) y promociones por volumen solo donde $ATE > 1.5x$. |
| **04_Operaciones_y_Planta.pbip** | **COO / Director de Enología** | Sub-absorción fabril por paradas ociosas de línea y mermas descontroladas en extracción y barricas. | • Absorción en equilibrio ($\pm 3\%$).<br>• Rendimiento extracción $\ge 70\%$.<br>• Merma ouillage $\le 2.0\%$.<br>• Cobertura secos $\ge 2.0$ meses. | **Matriz de Absorción Graduada:** Reasignación dinámica de turnos entre elaboración (CC-101) y fraccionamiento (CC-102). Humidificación de cava al 85% ante mermas $> 2.5\%$. |
| **06_Modelos_de_Riesgo_y_Prediccion.pbip** | **CRO / Comité de Riesgo** | Mora imprevista en exportaciones FOB, error de pronóstico de demanda lineal y vulnerabilidad ante shocks de cola. | • AUC-ROC Clasificación $\ge 0.85$.<br>• Reducción RMSE forecast $\ge 25\%$ vs SARIMAX.<br>• Buffer liquidez $\ge CVaR_{95}$ (\$24M). | **Scoring & Stress Testing:** Bloqueo de cuenta corriente a clientes FOB con Score $> 70$. Ejecución de coberturas ROFEX y warrants de stock ante Reverse Stress Breakpoint. |

---

## 3. Desglose Estratégico por Dominio de Negocio

### A. Módulo 02: Control de Gestión & Tesorería Bursátil
- **Usuario Persona:** *Gerente de Finanzas Corporativas / Head of FP&A*.
- **Mandato de Decisión:**
  1. *¿Por qué se desvió el margen bruto presupuestado?*  
     El módulo descompone la variación en Efecto Volumen ($EV$), Efecto Precio ($EP$) y Efecto Costo ($EC$). Si el desvío es por costo de insumos secos (botellas/corchos), se activa la renegociación contractual; si es por precio, se auditan las bonificaciones concedidas por la fuerza de ventas.
  2. *¿Cómo evitar costos financieros por descubierto y costos de oportunidad por caja parada?*  
     A través del **Modelo Estocástico de Miller-Orr (1966)** calibrado con la varianza diaria de cobros y pagos, el tesorero cuenta con un semáforo directo que indica diariamente si debe **comprar activos de renta fija (LECAPs/Money Market)** para capturar rendimientos o **rescatar fondos** para cubrir las obligaciones de nómina y proveedores sin fricciones de liquidez.

---

### B. Módulo 03: Inteligencia Comercial, Pricing & Pareto
- **Usuario Persona:** *Director Comercial / Revenue Management Lead*.
- **Mandato de Decisión:**
  1. *¿A qué clientes y productos debemos priorizar?*  
     La matriz de categorización **Pareto 80/20** clasifica los SKUs en Clase A, B y C. La regla de decisión prohíbe terminantemente los quiebres de stock en productos Clase A (que aportan el 80% de la masa de contribución marginal) y prescribe la racionalización o descontinuación de Clase C.
  2. *¿Es rentable otorgar un descuento del 15% a un hipermercado?*  
     El análisis econométrico de elasticidad precio determina si la demanda del segmento responderá con suficiente volumen para sobrecompensar el descuento. Si el segmento es inelástico ($\beta > -1.0$), el panel prohíbe el descuento; si es altamente elástico ($\beta < -2.0$), el panel aprueba la promoción condicionada a pedidos mínimos de 500 cajas.

---

### C. Módulo 04: Operaciones, Vendimia & Costos Fabriles
- **Usuario Persona:** *Gerente de Operaciones Industriales / Enólogo Principal*.
- **Mandato de Decisión:**
  1. *¿La planta está operando con capacidad ociosa o sobre-exigida?*  
     La **Matriz de Absorción Fabril Graduada** evalúa si el costo real incurrido en Molienda (CC-101) y Fraccionamiento (CC-102) coincide con los estándares absorbidos por litro o botella. Ante una sub-absorción $> +8\%$ (alerta roja), el director operativo reprograma turnos o adelanta el embotellado de líneas Reserva para diluir costos fijos.
  2. *¿Estamos perdiendo vino en el proceso de elaboración y guarda?*  
     El monitor de **Mermas Enológicas y Fabriles** compara los rendimientos de extracción de prensa neumática contra el target ($\ge 70\%$) y la evaporación en barricas (*ouillage*). Si la merma supera el 3.5%, el panel emite una orden directa para regular la humedad relativa de la cava al 85% e incrementar la frecuencia de relleno semanal.
  3. *¿Hay riesgo inminente de parada de línea de embotellado?*  
     El indicador de **Cobertura de Insumos Secos** proyecta las botellas y corchos disponibles en meses de operación. Si cae por debajo de 1.0 mes, se emite una alerta roja bloqueando el despacho hasta reponer stock de empaque.

---

### D. Módulo 06: Modelos de Riesgo, Machine Learning & Predicción
- **Usuario Persona:** *Chief Risk Officer / Comité de Inversiones / Quantitative Portfolio Manager*.
- **Mandato de Decisión:**
  1. *¿Cuál es el riesgo de default crediticio en la cartera de exportaciones?*  
     El clasificador binario supervisado (*Gradient Boosting / Random Forest*) asigna a cada cliente FOB una probabilidad de mora y un **Score de Riesgo (0-100)** calibrado según la Curva ROC ($AUC > 0.88$). A los clientes con Score $> 70$, el panel prescribe automáticamente exigir pago anticipado o retener el despacho de aduana.
  2. *¿Podemos confiar en el pronóstico de ventas para compras de uva a un año?*  
     El motor de **Forecasting Supervisado de Series de Tiempo** compite contra el benchmark clásico SARIMAX, incorporando estacionalidad por Fourier y variables macroeconómicas exógenas (IPC, FX, tasas). El reporte valida la reducción del error cuadrático medio ($RMSE$) para que el departamento de planificación opere con la predicción de menor sesgo.
  3. *¿Qué nivel de shock conjunto llevaría a la quiebra técnica a la empresa?*  
     A través de **10.000 simulaciones Monte Carlo**, el panel cuantifica el **Cash Flow at Risk (CF-VaR al 95% y 99%)** y el **Conditional VaR (Expected Shortfall)**. Adicionalmente, el **Reverse Stress Testing** define la frontera de insolvencia operativa (caída de ventas $> 38\%$, mora $> 50$ días y devaluación de insumos $> 55\%$), estableciendo el playbook de rescate financiero inmediato.
  4. *¿Cuál es el verdadero efecto causal de las campañas comerciales?*  
     Mediante **Double Machine Learning (DML)**, se aísla el Average Treatment Effect (ATE) de los descuentos eliminando el sesgo de confusión generado por variables macroeconómicas y de canal, permitiendo calibrar la política comercial sobre bases econométricas rigurosas.

---

## 4. Conclusión Institucional

Este esquema de trabajo garantiza que cada visualización en Power BI tenga un **dueño funcional claro, un umbral de tolerancia cuantitativo objetivo y una prescripción operativa inequívoca**, cumpliendo con los más altos estándares internacionales de gobierno de datos y control de gestión corporativo.
