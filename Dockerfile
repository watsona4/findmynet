FROM python:3.12-alpine AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.12-alpine

WORKDIR /app

COPY --from=builder /app/wheels /wheels

RUN pip install --no-cache --break-system-packages /wheels/*

RUN apk update && apk add speedtest-cli

COPY run_server.py .

LABEL org.opencontainers.image.source=https://github.com/watsona4/testmynet

CMD ["python3", "run_server.py"]
