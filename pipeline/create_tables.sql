-- ============================================================
-- Schema normalizado 3FN — NYC Yellow Taxi
-- ============================================================
-- Decisiones de diseño:
-- - trip_id es BIGSERIAL (surrogate key) porque la llave
--   natural no garantiza unicidad
-- - total_amount se omite: es atributo derivado (viola 3FN)
--   se calcula en DBT
-- - fact_trip referencia todas las dimensiones via FK
-- ============================================================

-- ── Dimensiones ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dim_vendor (
    vendor_id   INTEGER PRIMARY KEY,
    vendor_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_ratecode (
    ratecode_id   INTEGER PRIMARY KEY,
    ratecode_desc VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_payment_type (
    payment_type_id INTEGER PRIMARY KEY,
    payment_desc    VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_location (
    location_id  INTEGER PRIMARY KEY,
    borough      VARCHAR(100),
    zone         VARCHAR(100),
    service_zone VARCHAR(100)
);

-- ── Tabla de hechos ──────────────────────────────────────────

CREATE TABLE IF NOT EXISTS fact_trip (
    trip_id                BIGSERIAL    PRIMARY KEY,
    vendor_id              INTEGER      REFERENCES dim_vendor(vendor_id),
    tpep_pickup_datetime   TIMESTAMP,
    tpep_dropoff_datetime  TIMESTAMP,
    passenger_count        INTEGER,
    trip_distance          FLOAT,
    ratecode_id            INTEGER      REFERENCES dim_ratecode(ratecode_id),
    store_and_fwd_flag     VARCHAR(1),
    pu_location_id         INTEGER      REFERENCES dim_location(location_id),
    do_location_id         INTEGER      REFERENCES dim_location(location_id),
    payment_type           INTEGER      REFERENCES dim_payment_type(payment_type_id),
    fare_amount            FLOAT,
    extra                  FLOAT,
    mta_tax                FLOAT,
    tip_amount             FLOAT,
    tolls_amount           FLOAT,
    improvement_surcharge  FLOAT,
    congestion_surcharge   FLOAT,
    airport_fee            FLOAT
    -- total_amount excluido: dependencia transitiva
    -- se reconstruye en DBT como:
    -- fare_amount + extra + mta_tax + tip_amount +
    -- tolls_amount + improvement_surcharge +
    -- congestion_surcharge + airport_fee
);