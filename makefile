test:  ## 🎯 Unit tests for discord bot
	pytest -v

build:
	docker build --network=host -t sovia \
	    --build-arg HTTP_PROXY \
	    --build-arg HTTPS_PROXY \
	    --build-arg NO_PROXY \
	    .

run: build
	docker-compose up -d

start:
	docker-compose start

stop:
	docker-compose stop

restart: stop start

remove:
	docker-compose down
