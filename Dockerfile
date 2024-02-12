FROM python:latest
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . . 
CMD [ "flask", "--app", "stt-tracker", "run"]