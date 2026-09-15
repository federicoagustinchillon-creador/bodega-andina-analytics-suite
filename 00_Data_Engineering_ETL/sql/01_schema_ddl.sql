-- ===================================================================================
-- PROYECTO: Bodega & Agroindustria Andina S.A.
-- CAPA: 00_Data_Engineering_ETL - DDL Star Schema
-- AUTOR: Federico Agustin Chillon, UNCUYO
-- COMPATIBILIDAD: PostgreSQL / DuckDB
-- ===================================================================================

-- -----------------------------------------------------------------------------------
-- 1. DIMENSIONES
-- -----------------------------------------------------------------------------------

DROP TABLE IF EXISTS fact_ventas_reales CASCADE;
DROP TABLE IF EXISTS fact_presupuesto_ventas CASCADE;
DROP TABLE IF EXISTS fact_opex_mensual CASCADE;
DROP TABLE IF EXISTS fact_capital_trabajo CASCADE;
DROP TABLE IF EXISTS fact_operaciones_planta CASCADE;
DROP TABLE IF EXISTS fact_inventario_guarda CASCADE;
DROP TABLE IF EXISTS dim_cuentas_contables CASCADE;
DROP TABLE IF EXISTS dim_centros_costo CASCADE;
DROP TABLE IF EXISTS dim_productos CASCADE;
DROP TABLE IF EXISTS dim_calendario CASCADE;

-- Tabla de Calendario Institucional
CREATE TABLE dim_calendario (
    DateKey         INTEGER         PRIMARY KEY,
    Fecha           DATE            NOT NULL UNIQUE,
    Anio            INTEGER         NOT NULL CHECK (Anio >= 2020),
    MesNumero       INTEGER         NOT NULL CHECK (MesNumero BETWEEN 1 AND 12),
    MesNombre       VARCHAR(20)     NOT NULL,
    MesCorto        VARCHAR(10)     NOT NULL,
    Trimestre       VARCHAR(5)      NOT NULL CHECK (Trimestre IN ('T1', 'T2', 'T3', 'T4')),
    Semestre        VARCHAR(5)      NOT NULL CHECK (Semestre IN ('S1', 'S2')),
    EsFinDeSemana   INTEGER         NOT NULL CHECK (EsFinDeSemana IN (0, 1))
);

-- Catalogo Maestro de Productos y SKUs
CREATE TABLE dim_productos (
    ProductoID              VARCHAR(20)     PRIMARY KEY,
    SKU                     VARCHAR(50)     NOT NULL UNIQUE,
    Descripcion             VARCHAR(100)    NOT NULL,
    Linea                   VARCHAR(50)     NOT NULL,
    CostoEstandarUnit       NUMERIC(14,2)   NOT NULL CHECK (CostoEstandarUnit >= 0),
    PrecioPresupuestadoUnit NUMERIC(14,2)   NOT NULL CHECK (PrecioPresupuestadoUnit >= 0),
    CategoriaABC            VARCHAR(20)     NOT NULL CHECK (CategoriaABC IN ('Clase A', 'Clase B', 'Clase C'))
);

-- Estructura de Centros de Costo de Planta y Administracion
CREATE TABLE dim_centros_costo (
    CentroCostoID       VARCHAR(20)     PRIMARY KEY,
    NombreCentroCosto   VARCHAR(100)    NOT NULL,
    Area                VARCHAR(50)     NOT NULL,
    Responsable         VARCHAR(100)    NOT NULL
);

-- Plan de Cuentas Contable Corporativo
CREATE TABLE dim_cuentas_contables (
    CuentaID        VARCHAR(20)     PRIMARY KEY,
    NombreCuenta    VARCHAR(120)    NOT NULL,
    Naturaleza      VARCHAR(30)     NOT NULL CHECK (Naturaleza IN ('Ingresos', 'Costos', 'Gastos Operativos')),
    Rubro           VARCHAR(30)     NOT NULL CHECK (Rubro IN ('Revenue', 'COGS', 'OPEX'))
);

-- -----------------------------------------------------------------------------------
-- 2. TABLAS DE HECHOS (FACT TABLES)
-- -----------------------------------------------------------------------------------

-- Hechos de Facturacion y Ventas Reales (Extraccion SAP SD VBRK/VBRP)
CREATE TABLE fact_ventas_reales (
    TransaccionID   VARCHAR(50)     PRIMARY KEY,
    DateKey         INTEGER         NOT NULL,
    Fecha           DATE            NOT NULL,
    ProductoID      VARCHAR(20)     NOT NULL,
    CentroCostoID   VARCHAR(20)     NOT NULL,
    VolumenReal     NUMERIC(14,2)   NOT NULL CHECK (VolumenReal >= 0),
    PrecioRealUnit  NUMERIC(14,2)   NOT NULL CHECK (PrecioRealUnit >= 0),
    CostoRealUnit   NUMERIC(14,2)   NOT NULL CHECK (CostoRealUnit >= 0),
    IngresosReales  NUMERIC(14,2)   NOT NULL CHECK (IngresosReales >= 0),
    CostoReal       NUMERIC(14,2)   NOT NULL CHECK (CostoReal >= 0),
    MargenBrutoReal NUMERIC(14,2)   NOT NULL,
    CanalVenta      VARCHAR(50)     NOT NULL,
    CONSTRAINT fk_ventas_calendario FOREIGN KEY (DateKey) REFERENCES dim_calendario (DateKey),
    CONSTRAINT fk_ventas_producto   FOREIGN KEY (ProductoID) REFERENCES dim_productos (ProductoID),
    CONSTRAINT fk_ventas_cc         FOREIGN KEY (CentroCostoID) REFERENCES dim_centros_costo (CentroCostoID)
);

-- Hechos de Presupuesto Comercial Mensual
CREATE TABLE fact_presupuesto_ventas (
    DateKey                     INTEGER         NOT NULL,
    AnioMes                     VARCHAR(7)      NOT NULL,
    ProductoID                  VARCHAR(20)     NOT NULL,
    CentroCostoID               VARCHAR(20)     NOT NULL,
    VolumenPresupuestado        NUMERIC(14,2)   NOT NULL CHECK (VolumenPresupuestado >= 0),
    PrecioPresupuestadoUnit     NUMERIC(14,2)   NOT NULL CHECK (PrecioPresupuestadoUnit >= 0),
    CostoEstandarUnit           NUMERIC(14,2)   NOT NULL CHECK (CostoEstandarUnit >= 0),
    IngresosPresupuestados      NUMERIC(14,2)   NOT NULL CHECK (IngresosPresupuestados >= 0),
    CostoPresupuestado          NUMERIC(14,2)   NOT NULL CHECK (CostoPresupuestado >= 0),
    MargenBrutoPresupuestado    NUMERIC(14,2)   NOT NULL,
    PRIMARY KEY (DateKey, ProductoID, CentroCostoID),
    CONSTRAINT fk_pto_calendario    FOREIGN KEY (DateKey) REFERENCES dim_calendario (DateKey),
    CONSTRAINT fk_pto_producto      FOREIGN KEY (ProductoID) REFERENCES dim_productos (ProductoID),
    CONSTRAINT fk_pto_cc            FOREIGN KEY (CentroCostoID) REFERENCES dim_centros_costo (CentroCostoID)
);

-- Hechos de Gastos Operativos (OPEX)
CREATE TABLE fact_opex_mensual (
    DateKey             INTEGER         NOT NULL,
    AnioMes             VARCHAR(7)      NOT NULL,
    CentroCostoID       VARCHAR(20)     NOT NULL,
    CuentaID            VARCHAR(20)     NOT NULL,
    OPEXPresupuestado   NUMERIC(14,2)   NOT NULL CHECK (OPEXPresupuestado >= 0),
    OPEXReal            NUMERIC(14,2)   NOT NULL CHECK (OPEXReal >= 0),
    DesvioOPEX          NUMERIC(14,2)   NOT NULL,
    DesvioPorcentual    NUMERIC(10,4)   NOT NULL,
    PRIMARY KEY (DateKey, CentroCostoID, CuentaID),
    CONSTRAINT fk_opex_calendario   FOREIGN KEY (DateKey) REFERENCES dim_calendario (DateKey),
    CONSTRAINT fk_opex_cc           FOREIGN KEY (CentroCostoID) REFERENCES dim_centros_costo (CentroCostoID),
    CONSTRAINT fk_opex_cuenta       FOREIGN KEY (CuentaID) REFERENCES dim_cuentas_contables (CuentaID)
);

-- Hechos de Capital de Trabajo y Liquidez Operativa
CREATE TABLE fact_capital_trabajo (
    DateKey                     INTEGER         PRIMARY KEY,
    AnioMes                     VARCHAR(7)      NOT NULL UNIQUE,
    CuentasPorCobrar            NUMERIC(14,2)   NOT NULL CHECK (CuentasPorCobrar >= 0),
    CuentasPorPagar             NUMERIC(14,2)   NOT NULL CHECK (CuentasPorPagar >= 0),
    Inventario                  NUMERIC(14,2)   NOT NULL CHECK (Inventario >= 0),
    DSO_DiasCobro               NUMERIC(10,2)   NOT NULL CHECK (DSO_DiasCobro >= 0),
    DIO_DiasInventario          NUMERIC(10,2)   NOT NULL CHECK (DIO_DiasInventario >= 0),
    DPO_DiasPago                NUMERIC(10,2)   NOT NULL CHECK (DPO_DiasPago >= 0),
    CicloConversionEfectivo_CCC NUMERIC(10,2)   NOT NULL,
    NecesidadOperativaFondos_NOF NUMERIC(14,2)   NOT NULL,
    CONSTRAINT fk_cap_calendario FOREIGN KEY (DateKey) REFERENCES dim_calendario (DateKey)
);

-- Hechos de Molienda, Báscula y Rendimiento Enológico
CREATE TABLE fact_operaciones_planta (
    RemitoID                    VARCHAR(50)     PRIMARY KEY,
    DateKey                     INTEGER         NOT NULL,
    Fecha                       DATE            NOT NULL,
    CentroCostoID               VARCHAR(20)     NOT NULL,
    VariedadUva                 VARCHAR(50)     NOT NULL,
    FincaOrigen                 VARCHAR(100)    NOT NULL,
    KilosEntrada                NUMERIC(14,2)   NOT NULL CHECK (KilosEntrada > 0),
    GradosBrix                  NUMERIC(6,2)    NOT NULL CHECK (GradosBrix BETWEEN 10.0 AND 35.0),
    LitrosMostoObtenido         NUMERIC(14,2)   NOT NULL CHECK (LitrosMostoObtenido >= 0),
    RendimientoExtraccionPct    NUMERIC(6,2)    NOT NULL CHECK (RendimientoExtraccionPct BETWEEN 0.0 AND 100.0),
    CalificacionSanitaria       VARCHAR(30)     NOT NULL,
    UbicacionGeografica         VARCHAR(150)    NOT NULL,
    Latitud                     NUMERIC(9,4)    NOT NULL,
    Longitud                    NUMERIC(9,4)    NOT NULL,
    CONSTRAINT fk_planta_calendario FOREIGN KEY (DateKey) REFERENCES dim_calendario (DateKey),
    CONSTRAINT fk_planta_cc         FOREIGN KEY (CentroCostoID) REFERENCES dim_centros_costo (CentroCostoID)
);

-- Hechos de Inventario de Crianza, Guarda y Estiba de Bodega
CREATE TABLE fact_inventario_guarda (
    DateKey                     INTEGER         NOT NULL,
    AnioMes                     VARCHAR(7)      NOT NULL,
    ProductoID                  VARCHAR(20)     NOT NULL,
    TipoVasija                  VARCHAR(60)     NOT NULL,
    Litros                      NUMERIC(14,2)   NOT NULL CHECK (Litros >= 0),
    ValorInventario             NUMERIC(14,2)   NOT NULL CHECK (ValorInventario >= 0),
    MermaPct                    NUMERIC(8,4)    NOT NULL CHECK (MermaPct >= 0),
    DIODias                     NUMERIC(10,2)   NOT NULL CHECK (DIODias >= 0),
    EstadoCalidad               VARCHAR(40)     NOT NULL,
    PRIMARY KEY (DateKey, ProductoID, TipoVasija),
    CONSTRAINT fk_inv_calendario    FOREIGN KEY (DateKey) REFERENCES dim_calendario (DateKey),
    CONSTRAINT fk_inv_producto      FOREIGN KEY (ProductoID) REFERENCES dim_productos (ProductoID)
);
