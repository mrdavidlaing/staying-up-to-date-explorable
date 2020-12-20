FROM python:3.8-slim
RUN pip install pipenv
COPY Pipfile* /app/
RUN cd /app && pipenv lock --requirements > requirements.txt
RUN pip install -r /app/requirements.txt
COPY . /app/webroot/
WORKDIR /app/webroot/
EXPOSE 8080
CMD gunicorn --bind=0.0.0.0:8080 --workers=1 --threads=3 index:server