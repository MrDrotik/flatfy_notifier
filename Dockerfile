FROM python:3.9-slim


WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r requirements.txt


COPY src/* /app/

RUN chmod +x /app/main.py
RUN chmod +x /app/flatfy_articles_parser.py

ENV PYTHONPATH /app

CMD /app/main.py
