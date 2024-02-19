ARG STT_API_VERSION
FROM debian:bookworm
RUN apt install python pip firefox -y
ENV STT_API_SETTINGS=dict(TOKENS_DIR="/run/secrets/stt-api", STT_API_VERSION=$STT_API_VERSION)
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN mkdir /app
WORKDIR /app
COPY . . 
CMD  uwsgi --http 0.0.0.0:80 --master -p 4 -w stt-tracker:app