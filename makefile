test:  ## 🎯 Unit tests for discord bot
	pytest -v

build:
	docker build -t sovia .

run: build
	docker compose up -d

start:
	docker compose start

stop:
	docker compose stop

restart: stop start

remove:
	docker compose down
