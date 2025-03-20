FROM alpine:latest

WORKDIR /app

RUN apk update && apk add \
    speedtest-cli \
    py3-yaml \
    py3-paho-mqtt

COPY run_server.py .

LABEL org.opencontainers.image.source=https://github.com/watsona4/testmynet

CMD ["python3", "run_server.py"]
