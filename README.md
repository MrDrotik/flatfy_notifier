build:

```docker buildx build -t flatfy_parser --platform=linux/arm64,linux/amd64,linux/amd .```

run telegram bot server:

```docker run -p 8080:8080 -e TELEGRAM_BOT_TOKEN=[token] flatfy_parser```

run parser:

```docker run -e TELEGRAM_BOT_TOKEN=[token] flatfy_parser /app/src/flatfy_articles_parser.py```
