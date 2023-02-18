SHELL := /bin/bash
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
	python3 manage.py makemigrations

migrate: makemigrations
	python3 manage.py migrate

runserver: makemigrations migrate
	python3 manage.py runserver 8001

test:
	python3 manage.py test

init:
	packer init packer

fmt:
	packer fmt packer
	
validate: fmt
	packer validate packer

build: validate
	packer build packer/amazon-linux.pkr.hcl
