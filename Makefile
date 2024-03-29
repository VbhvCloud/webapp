SHELL := /bin/bash
VENV_NAME=venv

#
.EXPORT_ALL_VARIABLES:

POSTGRES_USER ?= webapp
POSTGRES_PASSWORD ?= webapp
POSTGRES_HOST ?= 127.0.0.1
POSTGRES_PORT ?= 5432
POSTGRES_DB ?= webapp
S3_BUCKET ?= test
DATABASE_URL?= postgres://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@$(POSTGRES_HOST):$(POSTGRES_PORT)/$(POSTGRES_DB)
AWS_REGION ?= us-east-1
SNS_TOPIC_ARN ?= test

# =============================================================================

makemigrations:
	python3 manage.py makemigrations

migrate: makemigrations
	python3 manage.py migrate

runserver: makemigrations migrate
	python3 manage.py runserver 0.0.0.0:8000

test:
	python3 manage.py test

init:
	packer init packer

fmt:
	packer fmt packer

validate: fmt
	packer validate packer

build: init validate
	packer build packer
