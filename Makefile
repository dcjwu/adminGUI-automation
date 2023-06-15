requirements:
	pipenv requirements > requirements.txt

build:
	docker build -t admin_script:latest .

run:
	docker run --name=script_container --env-file .env -it --rm admin_script:latest

.PHONY: requirements build run

