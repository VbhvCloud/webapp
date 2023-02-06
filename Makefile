SHELL := /bin/zsh
VENV_NAME=venv

#
.EXPORT_ALL_VARIABLES:

POSTGRES_USER ?= webapp
POSTGRES_PASSWORD ?= webapp
POSTGRES_HOST ?= 127.0.0.1
POSTGRES_PORT ?= 5432
POSTGRES_DB ?= webapp
DATABASE_URL?= postgres://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)

# =============================================================================

makemigrations:
	python manage.py makemigrations

migrate: makemigrations
	python manage.py migrate

runserver: makemigrations migrate
	python manage.py runserver

test:
	python manage.py test
