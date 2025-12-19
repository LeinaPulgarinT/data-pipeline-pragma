.PHONY: help setup up down run clean check all

# Variables
PYTHON := python3
VENV := venv
VENV_PYTHON := $(VENV)/bin/python
ZIP_PATH := ./data/data-prueba-data-engineer.zip

# Detectar si usar docker-compose (viejo) o docker compose (nuevo)
DOCKER_COMPOSE := $(shell which docker-compose 2>/dev/null || echo "docker compose")

help:
	@echo "Comandos disponibles:"
	@echo "  make all       - Ejecuta todo: setup + up + run"
	@echo "  make setup     - Crea ambiente virtual e instala dependencias"
	@echo "  make up        - Levanta PostgreSQL con Docker Compose"
	@echo "  make down      - Detiene y elimina contenedores de Docker"
	@echo "  make check     - Verifica que todo esté listo (DB arriba, ZIP en src/data/)"
	@echo "  make run       - Ejecuta el pipeline completo"
	@echo "  make clean     - Limpia datos temporales (CSVs descomprimidos, logs)"
	@echo ""
	@echo "Nota: Para activar el ambiente virtual manualmente: source $(VENV)/bin/activate"

setup:
	@echo "Configurando ambiente virtual..."
	@if [ ! -d "$(VENV)" ] || [ ! -f "$(VENV_PYTHON)" ] || ! $(VENV_PYTHON) -m pip --version > /dev/null 2>&1; then \
		echo "Creando/recreando ambiente virtual..."; \
		rm -rf $(VENV); \
		$(PYTHON) -m venv $(VENV); \
		$(VENV_PYTHON) -m ensurepip --upgrade 2>/dev/null || true; \
	fi
	@echo "Instalando dependencias en el ambiente virtual..."
	@$(VENV_PYTHON) -m pip install --upgrade pip
	@$(VENV_PYTHON) -m pip install -r requirements.txt
	@echo "Ambiente virtual creado y dependencias instaladas"
	@echo "Para activar el ambiente virtual manualmente: source $(VENV)/bin/activate"
up:
	@echo "Levantando PostgreSQL..."
	@$(DOCKER_COMPOSE) up -d db
	@echo "Esperando a que PostgreSQL esté listo..."
	@sleep 3
	@echo " PostgreSQL está corriendo"

down:
	@echo "Deteniendo contenedores..."
	@$(DOCKER_COMPOSE) down
	@echo " Contenedores detenidos"

check:
	@echo "Verificando entorno..."
	@echo "Verificando PostgreSQL..."
	@$(VENV_PYTHON) -c "import socket; s = socket.socket(); s.settimeout(1); result = s.connect_ex(('localhost', 5432)); s.close(); exit(0 if result == 0 else 1)" 2>/dev/null && echo "PostgreSQL está corriendo en el puerto 5432" || echo "PostgreSQL no responde. Asegúrate de ejecutar 'make up'"
	@test -f $(ZIP_PATH) && echo "Archivo ZIP encontrado en $(ZIP_PATH)" || (echo "Archivo ZIP no encontrado en $(ZIP_PATH). Por favor descárgalo manualmente." && exit 1)
	@test -d $(VENV) && echo " Ambiente virtual encontrado" || (echo "   Ambiente virtual no encontrado. Ejecuta 'make setup'" && exit 1)
	@$(VENV_PYTHON) -c "import pandas, sqlalchemy, psycopg2, yaml" 2>/dev/null && echo " Dependencias de Python instaladas" || (echo "   Faltan dependencias. Ejecuta 'make setup'" && exit 1)
	@echo "Todo está listo para ejecutar el pipeline"

run: check
	@echo "Ejecutando pipeline..."
	$(VENV_PYTHON) -m src.main

all: setup up run
	@echo "Pipeline ejecutado completamente"