all: build up

build:
	docker-compose build
	
up: down
	docker-compose up -d --build --remove-orphans

down:
	docker-compose down -t 1
