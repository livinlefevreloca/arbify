build:
	docker build -f Dockerfile.dev . -t arbify

build-no-cache:
	docker build --no-cache -f Dockerfile.dev . -t arbify

run:
	docker run -p 8000:8000 arbify

test:
	docker run arbify python -m pytest /app/tests/

shell:
	docker run -it arbify /bin/bash
