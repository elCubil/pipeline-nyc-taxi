🚕 NYC Yellow Taxi Data Pipeline

![DBT CI](https://github.com/elCubil/pipeline-nyc-taxi/actions/workflows/dbt_ci.yml/badge.svg)


Pipeline de ingeniería de datos para procesar viajes de NYC Yellow Taxi utilizando Python, PostgreSQL, Docker y dbt.

📌 Objetivo

Construir una solución de datos reproducible que permita:

Ingerir datos crudos de viajes de taxi.
Limpiar y validar información.
Normalizar el modelo a Tercera Forma Normal (3FN).
Aplicar transformaciones con dbt.
Generar tablas listas para análisis.

Este proyecto simula un flujo de trabajo real utilizado por equipos de Data Engineering.
***************************************************************************************
🏗 Arquitectura
NYC Taxi Dataset
        │
        ▼
Python Ingestion
        │
        ▼
PostgreSQL (Raw Layer)
        │
        ▼
DBT Models
        │
        ├── Staging
        ├── Intermediate
        └── Mart Layer
        │
        ▼
Analytics Ready Tables

***************************************************************************************
🛠 Tecnologías
Python
PostgreSQL
dbt
Docker
SQL
Git/GitHub

***************************************************************************************
📂 Capas del Proyecto
Raw Layer

Contiene los datos originales sin modificaciones.

Staging Layer
Limpieza de datos
Conversión de tipos
Estandarización de columnas
Eliminación de registros inválidos
Core Layer

Modelo normalizado en 3FN:

Trips
Vendors
Payment Types
Rate Codes
Locations
Mart Layer

Tablas optimizadas para análisis de negocio:

Viajes por día
Ingresos por zona
Distancia promedio
Métodos de pago
Horas pico

***************************************************************************************
✅ Calidad de Datos

Implementada con dbt tests:

Not Null
Unique
Relationships
Accepted Values

Ejemplo:

columns:
  - name: trip_id
    tests:
      - unique
      - not_null
***************************************************************************************
🚀 Cómo Ejecutar
1. Clonar repositorio
git clone https://github.com/elCubil/pipeline-nyc-taxi.git
cd pipeline-nyc-taxi
2. Levantar infraestructura
docker compose up -d
3. Ejecutar transformaciones
dbt run
4. Validar calidad
dbt test
***************************************************************************************
📊 Ejemplos de Análisis
Top zonas con mayor cantidad de viajes.
Ingresos por día.
Distribución de métodos de pago.
Distancia promedio por zona.
Tendencias horarias de demanda.

***************************************************************************************
🎯 Habilidades Demostradas

Este proyecto demuestra experiencia en:

Data Modeling (3FN)
SQL Avanzado
ETL/ELT
Data Warehousing
dbt
Docker
Data Quality
Git
PostgreSQL






