FROM python:3.12-rc-bookworm
ENV STT_API_VERSION=22
RUN mkdir /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
COPY . . 
CMD  uwsgi --http 0.0.0.0:80 --master -w stt-api:app