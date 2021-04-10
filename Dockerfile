FROM python:3.9-slim


WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install -r requirements.txt


COPY src /app/src

RUN mkdir /app/var

RUN chmod +x /app/src/main.py
RUN chmod +x /app/src/flatfy_articles_parser.py

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["/app/src/main.py"]
