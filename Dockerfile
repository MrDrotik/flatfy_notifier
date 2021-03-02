FROM python:3.9-slim


WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r requirements.txt


COPY ./database.py /app
COPY ./main.py /app
COPY ./models.py /app

RUN chmod +x /app/main.py

ENV PYTHONPATH /app

CMD /app/main.py
