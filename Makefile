build:
	docker build -t news .
run:
	docker run --network host -d news

up:
	docker build -t news .
	docker run --network host -d news