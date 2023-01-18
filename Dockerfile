FROM python:3.10

COPY . .

WORKDIR .
VOLUME /var/lib/docker/volumes/

RUN pip install -r requirements.txt

CMD ["python", "main.py"]

