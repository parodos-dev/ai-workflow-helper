FROM docker.io/python:3.11

WORKDIR /app/
COPY req.txt .
RUN pip install -r req.txt

ENTRYPOINT python main.py run
