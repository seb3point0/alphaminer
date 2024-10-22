build:
	docker-compose build

up:
	docker-compose up --build

start:
	docker-compose up -d --build

down:
	docker-compose down

install:
	docker-compose exec web poetry install

shell:
	docker-compose exec web bash

ps:
	docker-compose ps

logs-%:
	docker-compose logs $*

kill:
	docker-compose down --rmi all --volumes --remove-orphans

restart:
	docker-compose restart

rebuild:
	docker-compose up --build --force-recreate

clean:
	docker-compose down --volumes --remove-orphans

prune:
	docker system prune --all --volumes
