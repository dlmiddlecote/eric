NAME   := visit_aggregator
MODULE := visit_aggregator

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
	poetry run black -l 120 $(MODULE)

.PHONY: run
run:
	poetry run python -m $(MODULE) worker -l info

.PHONY: producer
producer:
	poetry run python -m $(MODULE) produce

.PHONY: docker
docker:
	docker build -t $(NAME):faust .

.PHONY: kind
kind:
	kind create cluster --name $(NAME) --image kindest/node:v1.14.10

.PHONY: load-image
load-image: docker
	kind load docker-image $(NAME):faust --name $(NAME)

.PHONY: k8s-kafka
k8s-kafka:
	kubectl --context kind-$(NAME) apply -R -f k8s/kafka

.PHONY: k8s-consumer
k8s-consumer:
	kubectl --context kind-$(NAME) apply -f k8s/consumer.yaml

.PHONY: k8s-producer
k8s-producer:
	kubectl --context kind-$(NAME) apply -f k8s/producer.yaml
