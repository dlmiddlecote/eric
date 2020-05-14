.PHONY: up
up: install
	docker-compose up -d

.PHONY: down
down:
	docker-compose down

.PHONY: install
install:
	poetry install

.PHONY: format
format:
	poetry run black -l 120 eric

.PHONY: run
run:
	poetry run python eric/app.py worker -l info

.PHONY: docker
docker:
	docker build -t eric:faust .
