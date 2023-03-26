FROM python:3.10-slim-buster

WORKDIR /src

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# COPY src .