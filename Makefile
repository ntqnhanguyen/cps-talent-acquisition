.PHONY: help build up down restart logs clean test

help:
	@echo "CPS Talent Acquisition System - Make Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs (all services)"
	@echo "  make logs-api    - View API logs"
	@echo "  make logs-db     - View database logs"
	@echo "  make logs-minio  - View MinIO logs"
	@echo "  make clean       - Stop services and remove volumes"
	@echo "  make ps          - Show service status"
	@echo "  make shell-api   - Open shell in API container"
	@echo "  make shell-db    - Open PostgreSQL shell"
	@echo "  make test        - Run tests"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Access:"
	@echo "  API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  MinIO Console: http://localhost:9001"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-db:
	docker-compose logs -f postgres

logs-minio:
	docker-compose logs -f minio

clean:
	docker-compose down -v
	@echo "All services stopped and volumes removed"

ps:
	docker-compose ps

shell-api:
	docker-compose exec api /bin/bash

shell-db:
	docker-compose exec postgres psql -U cps_user -d cps_talent_acquisition

test:
	docker-compose exec api pytest

