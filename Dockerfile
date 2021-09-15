FROM python:3.9

RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/

RUN pip install -r requirements.txt

ENV FLASK_APP=itca.api:app
ENTRYPOINT ["flask", "run", "-h", "0.0.0.0"]
