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