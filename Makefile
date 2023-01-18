requirements:
	pipenv requirements > requirements.txt

build-image:
	docker build -t admin_script:latest .

run:
	docker run --name=script_container --env-file .env -it admin_script:latest

start:
	docker start -i script_container

up: requirements build-image run

.PHONY: requirements build-image run up