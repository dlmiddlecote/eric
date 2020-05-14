.PHONY: bootstrap
bootstrap: install
	docker-compose up -d

.PHONY: install
install:
	poetry install

.PHONY: format
format:
	poetry run black -l 120 eric

.PHONY: run
run:
	poetry run python eric/app.py worker -l info
