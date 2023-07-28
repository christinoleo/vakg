FROM python:3.8-slim-bullseye
RUN apt-get update && apt-get install gcc libffi-dev libpq-dev -y && apt-get clean
RUN pip install spacy
RUN python -m spacy download en_core_web_md
WORKDIR /
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app
ENTRYPOINT uvicorn main:app --workers 1 --app-dir /app --port 5000 --host 0.0.0.0 --proxy-headers
