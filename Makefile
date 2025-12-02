.PHONY: help build up down logs restart shell clean

help:
	@echo "PXMX - Proxmox Administration Dashboard"
	@echo ""
	@echo "Available commands:"
	@echo "  make build         - Build containers"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make logs          - View logs (all services)"
	@echo "  make logs-web      - View web service logs"
	@echo "  make logs-celery   - View celery service logs"
	@echo "  make restart       - Restart all services"
	@echo "  make shell         - Open Django shell"
	@echo "  make bash          - Open bash in web container"
	@echo "  make migrate       - Run database migrations"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make sync          - Sync Proxmox clusters"
	@echo "  make clean         - Stop and remove all containers and volumes"
	@echo ""
	@echo "Use COMPOSE=docker-compose to use Docker instead of Podman"
	@echo "Example: make COMPOSE=docker-compose up"

# Default to podman-compose, but allow override
COMPOSE ?= podman-compose

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d
	@echo ""
	@echo "Application is starting..."
	@echo "Access at: http://localhost:8000"
	@echo "Admin login: admin / admin"
	@echo ""
	@echo "View logs with: make logs"

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

logs-web:
	$(COMPOSE) logs -f web

logs-celery:
	$(COMPOSE) logs -f celery

restart:
	$(COMPOSE) restart

shell:
	$(COMPOSE) exec web python manage.py shell

bash:
	$(COMPOSE) exec web bash

migrate:
	$(COMPOSE) exec web python manage.py migrate

createsuperuser:
	$(COMPOSE) exec web python manage.py createsuperuser

sync:
	$(COMPOSE) exec web python manage.py sync_proxmox --all

clean:
	$(COMPOSE) down -v
	@echo "All containers and volumes removed"

# Shortcuts
start: up
stop: down
