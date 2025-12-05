PYTHON=python
DOCKER_COMPOSE=docker compose
BACKEND_SERVICE=backend
MANAGE=./backend/manage.py

.PHONY: help up stop migrate makemigrations collectstatic worker test lint

help:
	@echo "Доступные команды:"
	@echo "  make up             - поднять сервисы через Docker Compose"
	@echo "  make stop           - остановить сервисы"
	@echo "  make migrate        - применить миграции"
	@echo "  make makemigrations - создать новые миграции"
	@echo "  make collectstatic  - собрать статику"
	@echo "  make worker  		 - запуск воркера Celery"
	@echo "  make test           - запустить тесты"
	@echo "  make lint           - проверить код flake8"

up:
	$(DOCKER_COMPOSE) up --build

stop:
	$(DOCKER_COMPOSE) down

migrate:
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) $(PYTHON) $(MANAGE) migrate

makemigrations:
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) $(PYTHON) $(MANAGE) makemigrations

collectstatic:
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) $(PYTHON) $(MANAGE) collectstatic --noinput && \
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) cp -r /app/collected_static/. /backend_static/static/

worker:
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) celery -A backend worker -l info

test:
	$(DOCKER_COMPOSE) exec -e CELERY_ALWAYS_EAGER=1 $(BACKEND_SERVICE) pytest

lint:
	$(DOCKER_COMPOSE) exec $(BACKEND_SERVICE) python -m flake8 backend/
