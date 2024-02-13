FROM python:latest
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN mkdir /app
WORKDIR /app
COPY . . 
CMD  uwsgi --http 0.0.0.0:80 --master -p 4 -w stt-tracker:app