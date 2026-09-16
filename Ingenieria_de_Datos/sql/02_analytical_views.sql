-- ===================================================================================
-- PROYECTO: Bodega & Agroindustria Andina S.A.
-- CAPA: Ingenieria_de_Datos - Analytical Views
-- AUTOR: Federico Agustin Chillon, UNCUYO
-- COMPATIBILIDAD: PostgreSQL / DuckDB
-- ===================================================================================

-- -----------------------------------------------------------------------------------
-- 1. VISTA P&L CASCADA MENSUAL CONSOLIDADA (REVENUE -> COGS -> MARGEN -> OPEX -> EBITDA)
-- -----------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_pl_cascada_mensual;

CREATE VIEW vw_pl_cascada_mensual AS
WITH ventas_mensuales AS (
    SELECT
        c.Anio,
        c.MesNumero,
        CONCAT(CAST(c.Anio AS VARCHAR), '-', LPAD(CAST(c.MesNumero AS VARCHAR), 2, '0')) AS AnioMes,
        MIN(v.DateKey) AS DateKey,
        SUM(v.IngresosReales) AS IngresosReales,
        SUM(v.CostoReal) AS COGSReal,
        SUM(v.MargenBrutoReal) AS MargenBrutoReal
    FROM fact_ventas_reales v
    INNER JOIN dim_calendario c ON v.DateKey = c.DateKey
    GROUP BY c.Anio, c.MesNumero
),
pto_mensual AS (
    SELECT
        AnioMes,
        MIN(DateKey) AS DateKey,
        SUM(IngresosPresupuestados) AS IngresosPresupuestados,
        SUM(CostoPresupuestado) AS COGSPresupuestado,
        SUM(MargenBrutoPresupuestado) AS MargenBrutoPresupuestado
    FROM fact_presupuesto_ventas
    GROUP BY AnioMes
),
opex_mensual AS (
    SELECT
        AnioMes,
        SUM(OPEXPresupuestado) AS OPEXPresupuestado,
        SUM(OPEXReal) AS OPEXReal,
        SUM(DesvioOPEX) AS DesvioOPEX
    FROM fact_opex_mensual
    GROUP BY AnioMes
)
SELECT
    COALESCE(vm.AnioMes, pm.AnioMes) AS AnioMes,
    COALESCE(vm.DateKey, pm.DateKey) AS DateKey,
    
    -- Ingresos por Ventas
    ROUND(COALESCE(vm.IngresosReales, 0), 2) AS IngresosReales,
    ROUND(COALESCE(pm.IngresosPresupuestados, 0), 2) AS IngresosPresupuestados,
    ROUND(COALESCE(vm.IngresosReales, 0) - COALESCE(pm.IngresosPresupuestados, 0), 2) AS DesvioIngresos,
    
    -- Costo de Mercaderias Vendidas (COGS)
    ROUND(COALESCE(vm.COGSReal, 0), 2) AS COGSReal,
    ROUND(COALESCE(pm.COGSPresupuestado, 0), 2) AS COGSPresupuestado,
    ROUND(COALESCE(vm.COGSReal, 0) - COALESCE(pm.COGSPresupuestado, 0), 2) AS DesvioCOGS,
    
    -- Margen Bruto
    ROUND(COALESCE(vm.MargenBrutoReal, 0), 2) AS MargenBrutoReal,
    ROUND(COALESCE(pm.MargenBrutoPresupuestado, 0), 2) AS MargenBrutoPresupuestado,
    ROUND(COALESCE(vm.MargenBrutoReal, 0) - COALESCE(pm.MargenBrutoPresupuestado, 0), 2) AS DesvioMargenBruto,
    
    ROUND(CASE 
        WHEN COALESCE(vm.IngresosReales, 0) > 0 
        THEN (COALESCE(vm.MargenBrutoReal, 0) / vm.IngresosReales) * 100.0 
        ELSE 0.0 
    END, 2) AS MargenBrutoRealPct,
    
    ROUND(CASE 
        WHEN COALESCE(pm.IngresosPresupuestados, 0) > 0 
        THEN (COALESCE(pm.MargenBrutoPresupuestado, 0) / pm.IngresosPresupuestados) * 100.0 
        ELSE 0.0 
    END, 2) AS MargenBrutoPresupuestoPct,
    
    -- Gastos Operativos (OPEX)
    ROUND(COALESCE(om.OPEXReal, 0), 2) AS OPEXReal,
    ROUND(COALESCE(om.OPEXPresupuestado, 0), 2) AS OPEXPresupuestado,
    ROUND(COALESCE(om.DesvioOPEX, 0), 2) AS DesvioOPEX,
    
    -- EBITDA
    ROUND(COALESCE(vm.MargenBrutoReal, 0) - COALESCE(om.OPEXReal, 0), 2) AS EBITDAReal,
    ROUND(COALESCE(pm.MargenBrutoPresupuestado, 0) - COALESCE(om.OPEXPresupuestado, 0), 2) AS EBITDAPresupuestado,
    ROUND((COALESCE(vm.MargenBrutoReal, 0) - COALESCE(om.OPEXReal, 0)) - (COALESCE(pm.MargenBrutoPresupuestado, 0) - COALESCE(om.OPEXPresupuestado, 0)), 2) AS DesvioEBITDA,
    
    ROUND(CASE 
        WHEN COALESCE(vm.IngresosReales, 0) > 0 
        THEN ((COALESCE(vm.MargenBrutoReal, 0) - COALESCE(om.OPEXReal, 0)) / vm.IngresosReales) * 100.0 
        ELSE 0.0 
    END, 2) AS MargenEBITDARealPct,

    ROUND(CASE 
        WHEN COALESCE(pm.IngresosPresupuestados, 0) > 0 
        THEN ((COALESCE(pm.MargenBrutoPresupuestado, 0) - COALESCE(om.OPEXPresupuestado, 0)) / pm.IngresosPresupuestados) * 100.0 
        ELSE 0.0 
    END, 2) AS MargenEBITDAPresupuestoPct

FROM ventas_mensuales vm
FULL OUTER JOIN pto_mensual pm ON vm.AnioMes = pm.AnioMes
LEFT JOIN opex_mensual om ON COALESCE(vm.AnioMes, pm.AnioMes) = om.AnioMes;

-- -----------------------------------------------------------------------------------
-- 2. VISTA ANALISIS PARETO (80/20) COMERCIAL POR PRODUCTO Y CANAL
-- -----------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_analisis_pareto_comercial;

CREATE VIEW vw_analisis_pareto_comercial AS
WITH resumen_comercial AS (
    SELECT
        p.ProductoID,
        p.SKU,
        p.Descripcion,
        p.Linea,
        v.CanalVenta,
        SUM(v.VolumenReal) AS VolumenTotal,
        SUM(v.IngresosReales) AS IngresosTotales,
        SUM(v.CostoReal) AS CostoTotal,
        SUM(v.MargenBrutoReal) AS MargenBrutoTotal
    FROM fact_ventas_reales v
    INNER JOIN dim_productos p ON v.ProductoID = p.ProductoID
    GROUP BY p.ProductoID, p.SKU, p.Descripcion, p.Linea, v.CanalVenta
),
totales_globales AS (
    SELECT SUM(IngresosTotales) AS GranTotalIngresos FROM resumen_comercial
),
acumulado AS (
    SELECT
        rc.ProductoID,
        rc.SKU,
        rc.Descripcion,
        rc.Linea,
        rc.CanalVenta,
        rc.VolumenTotal,
        ROUND(rc.IngresosTotales, 2) AS IngresosTotales,
        ROUND(rc.MargenBrutoTotal, 2) AS MargenBrutoTotal,
        ROUND((rc.IngresosTotales / tg.GranTotalIngresos) * 100.0, 2) AS ParticipacionVentasPct,
        ROUND((SUM(rc.IngresosTotales) OVER (ORDER BY rc.IngresosTotales DESC) / tg.GranTotalIngresos) * 100.0, 2) AS PctAcumuladoVentas,
        ROW_NUMBER() OVER (ORDER BY rc.IngresosTotales DESC) AS RankingComercial
    FROM resumen_comercial rc
    CROSS JOIN totales_globales tg
)
SELECT
    RankingComercial,
    ProductoID,
    SKU,
    Descripcion,
    Linea,
    CanalVenta,
    VolumenTotal,
    IngresosTotales,
    MargenBrutoTotal,
    ParticipacionVentasPct,
    PctAcumuladoVentas,
    CASE
        WHEN PctAcumuladoVentas <= 80.0 THEN 'Clase A (Top 80%)'
        WHEN PctAcumuladoVentas <= 95.0 THEN 'Clase B (80%-95%)'
        ELSE 'Clase C (Cola 95%-100%)'
    END AS ClasificacionPareto
FROM acumulado;

-- -----------------------------------------------------------------------------------
-- 3. VISTA EFICIENCIA ENOLOGICA Y RENDIMIENTO AGROINDUSTRIAL DE PLANTA
-- -----------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_eficiencia_enologica_planta;

CREATE VIEW vw_eficiencia_enologica_planta AS
SELECT
    FincaOrigen,
    VariedadUva,
    COUNT(RemitoID) AS TotalRemitosIngresados,
    ROUND(SUM(KilosEntrada), 2) AS TotalKilosEntrada,
    ROUND(AVG(GradosBrix), 2) AS PromedioGradosBrix,
    ROUND(SUM(LitrosMostoObtenido), 2) AS TotalLitrosMostoObtenido,
    ROUND((SUM(LitrosMostoObtenido) / SUM(KilosEntrada)) * 100.0, 2) AS RendimientoPromedioExtraccionPct,
    
    ROUND(SUM(CASE WHEN CalificacionSanitaria = 'Optima' THEN 1 ELSE 0 END) * 100.0 / COUNT(RemitoID), 2) AS PorcentajeSanidadOptima,
    ROUND(SUM(CASE WHEN CalificacionSanitaria = 'Buena' THEN 1 ELSE 0 END) * 100.0 / COUNT(RemitoID), 2) AS PorcentajeSanidadBuena,
    ROUND(SUM(CASE WHEN CalificacionSanitaria NOT IN ('Optima', 'Buena') THEN 1 ELSE 0 END) * 100.0 / COUNT(RemitoID), 2) AS PorcentajeSanidadRegular,

    CASE
        WHEN (SUM(LitrosMostoObtenido) / SUM(KilosEntrada)) * 100.0 >= 72.0 THEN 'Alta Eficiencia Enologica'
        WHEN (SUM(LitrosMostoObtenido) / SUM(KilosEntrada)) * 100.0 >= 69.0 THEN 'Rendimiento Estandar Bodega'
        ELSE 'Baja Extraccion / Alerta Operativa'
    END AS DiagnosticoRendimiento
FROM fact_operaciones_planta
GROUP BY FincaOrigen, VariedadUva;
