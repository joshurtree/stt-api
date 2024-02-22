ARG STT_API_VERSION
FROM debian:bookworm
RUN apt update
RUN apt install python3-pip firefox-esr -y
RUN apt install -y python3.11-venv
RUN mkdir /app
WORKDIR /app
COPY requirements.txt requirements.txt
RUN python3 -m venv .venv
ENV PATH=".venv/bin:$PATH"
RUN pip install -r requirements.txt
COPY . . 
CMD  uwsgi --http 0.0.0.0:80 --master -file stt-api:app