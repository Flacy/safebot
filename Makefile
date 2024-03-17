env_prefix := env/.env.
docker_dev := -f docker-compose.yml -f docker-compose.dev.yml

clean:
	rm -f .env # ignore not exist error

env: clean
	ln -s $(env_prefix)prod .env

env-dev: clean
	ln -s $(env_prefix)dev .env

build:
	docker-compose build app

build-dev:
	docker-compose build --build-arg dev=true app

run: env
	docker-compose up -d app

run-dev: env-dev
	docker-compose $(docker_dev) up app

test:
	docker-compose $(docker_dev) run app pytest -W ignore

bash:
	docker-compose $(docker_dev) run app bash

logs:
	docker logs safebot_app

.SILENT: