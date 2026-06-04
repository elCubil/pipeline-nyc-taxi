#!/usr/bin/env python
# coding: utf-8

import click
import duckdb
import pandas as pd
import requests
import os
from sqlalchemy import create_engine, text
from tqdm.auto import tqdm

# ── Catálogos fijos (conocimiento del dominio NYC Taxi) ──────
# Estos valores son estables, documentados por NYC TLC
# Fuente: https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf

VENDORS = {
    1: "Creative Mobile Technologies",
    2: "VeriFone Inc.",
    0: "Unknown"
}

RATECODES = {
    1: "Standard rate",
    2: "JFK",
    3: "Newark",
    4: "Nassau or Westchester",
    5: "Negotiated fare",
    6: "Group ride",
    99: "Unknown"
}

PAYMENT_TYPES = {
    1: "Credit card",
    2: "Cash",
    3: "No charge",
    4: "Dispute",
    5: "Unknown",
    6: "Voided trip",
    0: "Unknown"
}

# ── Crea las tablas 3FN en Postgres ─────────────────────────
def create_schema(engine):
    sql_path = os.path.join(os.path.dirname(__file__), "create_tables.sql")
    with open(sql_path) as f:
        sql = f.read()
    with engine.begin() as conn:
        conn.execute(text(sql))
    print("✓ Schema 3FN creado")

# ── Carga dim_vendor, dim_ratecode, dim_payment_type ────────
# Estas tablas son pequeñas y sus valores vienen de los
# catálogos definidos arriba, no del parquet
def load_dimensions(engine):
    print("Cargando dimensiones...")

    with engine.begin() as conn:

        for vid, vname in VENDORS.items():
            conn.execute(text("""
                INSERT INTO dim_vendor (vendor_id, vendor_name)
                VALUES (:id, :name)
                ON CONFLICT (vendor_id) DO NOTHING
            """), {"id": vid, "name": vname})

        for rid, rdesc in RATECODES.items():
            conn.execute(text("""
                INSERT INTO dim_ratecode (ratecode_id, ratecode_desc)
                VALUES (:id, :desc)
                ON CONFLICT (ratecode_id) DO NOTHING
            """), {"id": rid, "desc": rdesc})

        for pid, pdesc in PAYMENT_TYPES.items():
            conn.execute(text("""
                INSERT INTO dim_payment_type (payment_type_id, payment_desc)
                VALUES (:id, :desc)
                ON CONFLICT (payment_type_id) DO NOTHING
            """), {"id": pid, "desc": pdesc})

    print("✓ dim_vendor, dim_ratecode, dim_payment_type cargadas")

# ── Carga dim_location desde archivo oficial NYC TLC ────────
# NYC publica un CSV con los nombres de las 265 zonas
# Fuente: https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
def load_locations(engine):
    url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
    print("Descargando zonas NYC...")

    df = pd.read_csv(url)
    df.columns = ["location_id", "borough", "zone", "service_zone"]

    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO dim_location
                    (location_id, borough, zone, service_zone)
                VALUES (:lid, :borough, :zone, :service_zone)
                ON CONFLICT (location_id) DO NOTHING
            """), {
                "lid":          row["location_id"],
                "borough":      row["borough"],
                "zone":         row["zone"],
                "service_zone": row["service_zone"]
            })

    print(f"✓ {len(df)} zonas cargadas en dim_location")



# ── Descarga el parquet mensual de NYC TLC ───────────────────
# URL oficial: https://d37ci6vzurychx.cloudfront.net/trip-data/
def download_parquet(year: int, month: int, dest_folder: str) -> str:
    base     = "https://d37ci6vzurychx.cloudfront.net/trip-data"
    filename = f"yellow_tripdata_{year}-{month:02d}.parquet"
    url      = f"{base}/{filename}"
    dest     = os.path.join(dest_folder, filename)

    if os.path.exists(dest):
        print(f"Ya existe: {filename}, saltando descarga")
        return dest

    print(f"Descargando {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(dest, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✓ Descargado: {filename}")
    return dest

# ── Normaliza y carga fact_trip en chunks ────────────────────
# Aquí se aplica 3FN:
#   - Se renombran columnas para consistencia (snake_case)
#   - Se excluye total_amount (atributo derivado, viola 3FN)
#   - DuckDB lee el parquet eficientemente por columnas
def load_fact_trip(parquet_path: str, engine, chunksize: int):
    print("Normalizando y cargando fact_trip...")

    duck = duckdb.connect()
    duck.execute(f"""
        CREATE VIEW raw AS
        SELECT * FROM read_parquet('{parquet_path}')
    """)

    total = duck.execute("""
        SELECT COUNT(*) FROM raw
        WHERE RatecodeID IN (1,2,3,4,5,6,99)
          AND VendorID IN (0,1,2)
          AND payment_type IN (0,1,2,3,4,5,6)
    """).fetchone()[0]
    print(f"  Total filas válidas: {total:,}")

    offset = 0
    pbar   = tqdm(total=total, unit="filas")

    while True:
        df = duck.execute(f"""
            SELECT
                VendorID               AS vendor_id,
                tpep_pickup_datetime,
                tpep_dropoff_datetime,
                passenger_count,
                trip_distance,
                RatecodeID             AS ratecode_id,
                store_and_fwd_flag,
                PULocationID           AS pu_location_id,
                DOLocationID           AS do_location_id,
                payment_type,
                fare_amount,
                extra,
                mta_tax,
                tip_amount,
                tolls_amount,
                improvement_surcharge,
                congestion_surcharge,
                Airport_fee            AS airport_fee
                -- total_amount excluido: dependencia transitiva
                -- se calcula en DBT
            FROM raw
            WHERE RatecodeID IN (1,2,3,4,5,6,99)
              AND VendorID IN (0,1,2)
              AND payment_type IN (0,1,2,3,4,5,6)
            LIMIT {chunksize} OFFSET {offset}
        """).df()

        if df.empty:
            break

        df.to_sql(
            name      = "fact_trip",
            con       = engine,
            if_exists = "append",
            index     = False
        )

        offset += len(df)
        pbar.update(len(df))

    pbar.close()
    duck.close()
    print(f"✓ fact_trip cargada: {offset:,} filas")

# ── CLI ──────────────────────────────────────────────────────
@click.command()
@click.option('--pg-user',   default='root',     help='PostgreSQL user')
@click.option('--pg-pass',   default='root',     help='PostgreSQL password')
@click.option('--pg-host',   default='localhost', help='PostgreSQL host')
@click.option('--pg-port',   default=5432,        help='PostgreSQL port', type=int)
@click.option('--pg-db',     default='ny_taxi',   help='PostgreSQL database')
@click.option('--year',      default=2024,        help='Year to download', type=int)
@click.option('--month',     default=1,           help='Month to download', type=int)
@click.option('--chunksize', default=100000,      help='Rows per chunk', type=int)
def ejecuta(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize):

    print(f"\n🚕 NYC Taxi Pipeline — {year}-{month:02d}")
    print(f"   Destino: {pg_host}:{pg_port}/{pg_db}\n")

    engine = create_engine(
        f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    )

    # Paso 1 — Schema 3FN
    create_schema(engine)

    # Paso 2 — Dimensiones fijas
    load_dimensions(engine)

    # Paso 3 — Zonas NYC
    load_locations(engine)

    # Paso 4 — Descarga parquet
    os.makedirs("/tmp/taxi_data", exist_ok=True)
    parquet_path = download_parquet(year, month, "/tmp/taxi_data")

    # Paso 5 — fact_trip normalizada
    load_fact_trip(parquet_path, engine, chunksize)

    print(f"\n✅ Pipeline completo: {year}-{month:02d} cargado en {pg_db}\n")


if __name__ == '__main__':
    ejecuta()