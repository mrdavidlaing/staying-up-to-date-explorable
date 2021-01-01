# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.8-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Install dependencies - is a separate layer to speed up future builds
RUN pip install pipenv
COPY Pipfile* /app/
RUN cd /app && pipenv lock --requirements > requirements.txt
RUN pip install -r /app/requirements.txt

# Copy and setup Dash app to run via gunicorn listening on $PORT (normally 8080)
COPY . /app/webroot/
WORKDIR /app/webroot/
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 index:server