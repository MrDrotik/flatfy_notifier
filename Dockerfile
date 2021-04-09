FROM python:3.9-slim


WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r requirements.txt


COPY ./command_handlers.py /app
COPY ./database.py /app
COPY ./flatfy_articles_parser.py /app
COPY ./main.py /app
COPY ./models.py /app
COPY ./telegram_api.py /app
COPY ./views.py /app

RUN chmod +x /app/main.py
RUN chmod +x /app/parser.py

ENV PYTHONPATH /app

CMD /app/main.py
