FROM python:latest
RUN apt install nginx
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . . 
CMD [ "uwsgi", "--http", "127.0.0.1:80", "--master", "-p 4", "-w stt-tracker:app"]