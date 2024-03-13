docker_dev := -f docker-compose.yml -f docker-compose.dev.yml

build:
	docker-compose build app

build-dev:
	docker-compose build --build-arg dev=true app

test:
	docker-compose $(docker_dev) run app pytest -W ignore

run:
	docker-compose up -d app

run-dev:
	docker-compose $(docker_dev) up app

bash:
	docker-compose $(docker_dev) run app bash