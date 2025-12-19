# Data Pipeline: Data Rangers

Este proyecto implementa un pipeline de datos que carga archivos CSV de manera incremental, los procesa en micro-batches, los almacena en una base de datos relacional y mantiene estadísticas incrementales sin recalcular los datos históricos.

El pipeline fue diseñado para cumplir explícitamente con los requerimientos del reto técnico, priorizando eficiencia, claridad y buenas prácticas de ingeniería de datos.
## Estructura del Proyecto

```
data-pipeline
├── src
│   ├── main.py                # Punto de entrada del pipeline
│   ├── pipeline.py            # Orquestación del flujo ETL
│   ├── logging.py             # Configuración de logs
│   ├── etl
│   │   ├── extract.py         # Lectura de CSV por micro-batches
│   │   ├── transforms.py      # Normalización y reglas de negocio
│   │   └── load.py            # Inserción en base de datos
│   ├── db
│   │   ├── repository.py      # Acceso y persistencia en la base de datos
│   ├── stats
│   │   ├── recorder.py        # Cálculo incremental de estadísticas
│   └── data
│       └── data-prueba-data-engineer.zip
├── docker-compose.yml         # PostgreSQL para entorno local
├── Dockerfile
├── requirements.txt
├── pyproject.toml
├── Makefile
└── README.md
```

## Características Principales

**Carga incremental de CSV**
  - Procesa todos los archivos CSV excepto `validation.csv`
  - Nunca carga todos los archivos simultáneamente en memoria

**Procesamiento por micro-batches**
  - Lectura y carga en bloques configurables
  - Control explícito del uso de memoria

**Persistencia en base de datos**
  - Base de datos PostgreSQL
  - Prevención de duplicados mediante constraints y `ON CONFLICT DO NOTHING`

**Manejo de valores nulos**
  - Los valores nulos en `price` son imputados usando la mediana del batch
  - Garantiza consistencia y evita duplicados por valores `NULL`

**Estadísticas incrementales**
  - Recuento de filas insertadas
  - Promedio, mínimo y máximo de `price`
  - Las estadísticas se actualizan **solo con nuevos datos**
  - No se recalculan datos históricos desde la base de datos

**Logs claros y orientados al negocio**
  - Resumen por archivo procesado
  - Información útil sin ruido innecesario

## Ejemplo de Logs
Durante la ejecución del pipeline, se generan logs informativos por cada archivo procesado, incluyendo métricas de lectura, inserción, duplicados y tiempo de procesamiento.

Ejemplo de salida:

```
Procesando archivo: 2012-1.csv
Archivo 2012-1.csv | leídas=22 | insertadas=22 | ignoradas=0 | tiempo=91 ms

Procesando archivo: 2012-2.csv
Archivo 2012-2.csv | leídas=29 | insertadas=29 | ignoradas=0 | tiempo=109 ms
```

Al finalizar cada fase, se imprimen las estadisticas acumuladas tanto en memoria como en la base de datos:

```
Estadísticas en ejecución (memoria) después de 2012-1..5:
{'row_count': 143, 'sum_price': 8297.0, 'min_price': 10.0, 'max_price': 100.0, 'average_price': 58.02}

Estadísticas en base de datos después de 2012-1..5:
{'row_count': 143, 'average_price': 58.02, 'min_price': 10, 'max_price': 100}
```

## Cómo Ejecutar el Pipeline

### Requisitos

- Python 3.12+
- Docker y Docker Compose

### Ejecución Completa

```
make all
```

Esto realiza:
1. Creación del entorno virtual
2. Instalación de dependencias
3. Levantamiento de PostgreSQL
4. Ejecución del pipeline completo

## Validacion

El archivo `validation.csv` no forma parte de la carga inicial de datos.  
Se ejecuta posteriormente a través del mismo pipeline con fines de validación.

El objetivo de esta fase es verificar que:

- El pipeline es **idempotente**.
- Los registros que ya existen en la base de datos **no se duplican** gracias a la restricción de unicidad y al uso de `ON CONFLICT DO NOTHING`.
- Los registros **nuevos** presentes en `validation.csv` se insertan correctamente.
- Las estadísticas en ejecución (conteo, promedio, mínimo y máximo de `price`) se actualizan únicamente en función de los registros efectivamente insertados.

Este comportamiento permite simular un escenario real de ingesta incremental, donde nuevos eventos pueden llegar junto con eventos ya procesados previamente.

