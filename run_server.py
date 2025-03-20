import os
import json
import logging
import random
import signal
import time
from datetime import timedelta
from subprocess import run

import paho.mqtt.client as mqtt
import yaml

logging.basicConfig(
    format="%(asctime)s [%(levelname)s]: %(message)s", level=logging.DEBUG
)

path = "/root/run-server/config/config.yaml"
if os.path.exists(path):
    with open(path, "rb") as f:
        config = yaml.safe_load(f)
else:
    with open("config.yaml", "rb") as f:
        config = yaml.safe_load(f)

logging.info("%s", config)

e = 2.718281828459045

client = mqtt.Client()
client.enable_logger()

cmd = ["speedtest-cli", "--json"]

logging.debug("cmd: %s", cmd)

logging.info(
    "Connecting to %s:%d", config["mqtt"]["server"], int(config["mqtt"]["port"])
)

client.connect(config["mqtt"]["server"], int(config["mqtt"]["port"]), 60)
client.loop_start()


def handler(signum, frame):
    client.disconnect()
    client.loop_stop()
    sys.exit(0)


signal.signal(signal.SIGTERM, handler)

if "distribution" not in config:
    mean = 3600
    stdev = 900
else:
    mean = config["distribution"].get("mean", 3600)
    stdev = config["distribution"].get("stdev", 900)

logging.debug("mean = %f, stdev = %f", mean, stdev)

base_sensor = {
    "device": {
        "name": "Speedtest",
        "manufacturer": "Ookla",
        "model": "speedtest-cli",
        "sw_version": "2.1.3",
        "identifiers": ["773e24ab-3d14-4341-ac6a-67f0687d9b50"],
    },
    "state_topic": "speedtest/status",
}

client.publish(
    "homeassistant/sensor/speedtest/download/config",
    json.dumps(
        base_sensor
        | {
            "name": "Download Rate",
            "icon": "mdi:download",
            "unique_id": "6fc0d13b-ffe4-47e5-8206-994b186d7f5d",
            "device_class": "data_rate",
            "unit_of_measurement": "Mbit/s",
            "value_template": "{{ value_json.download/1000000 }}",
        }
    ),
    retain=True,
)

client.publish(
    "homeassistant/sensor/speedtest/upload/config",
    json.dumps(
        base_sensor
        | {
            "name": "Upload Rate",
            "icon": "mdi:upload",
            "unique_id": "61d903a7-c986-422b-82a0-1634aef43413",
            "device_class": "data_rate",
            "unit_of_measurement": "Mbit/s",
            "value_template": "{{ value_json.upload/1000000 }}",
        }
    ),
    retain=True,
)

client.publish(
    "homeassistant/sensor/speedtest/ping/config",
    json.dumps(
        base_sensor
        | {
            "name": "Ping",
            "icon": "mdi:timer-outline",
            "unique_id": "0e64a93a-73a1-4800-a0e5-5b9cb5edbb6d",
            "device_class": "duration",
            "unit_of_measurement": "s",
            "value_template": "{{ value_json.ping/1000 }}",
        }
    ),
    retain=True,
)

client.publish(
    "homeassistant/sensor/speedtest/server/config",
    json.dumps(
        base_sensor
        | {
            "name": "Server",
            "unique_id": "7dbda893-dd34-4ca9-aa6e-f511bb0ace9a",
            "json_attributes_topic": "speedtest/status",
            "json_attributes_template": "{{ value_json.server|tojson }}",
            "value_template": "{{ value_json.server.name }}",
        }
    ),
    retain=True,
)

client.publish(
    "homeassistant/sensor/speedtest/timestamp/config",
    json.dumps(
        base_sensor
        | {
            "name": "Timestamp",
            "unique_id": "fe0258e4-f964-49ef-90f3-783bbe93b004",
            "device_class": "timestamp",
            "value_template": "{{ value_json.timestamp }}",
        }
    ),
    retain=True,
)

client.publish(
    "homeassistant/sensor/speedtest/bytes_sent/config",
    json.dumps(
        base_sensor
        | {
            "name": "Bytes Sent",
            "unique_id": "69f1f446-184b-4771-8d27-0241f36836f4",
            "device_class": "data_size",
            "unit_of_measurement": "MB",
            "value_template": "{{ value_json.bytes_sent/1024/1024 }}",
        }
    ),
    retain=True,
)

client.publish(
    "homeassistant/sensor/speedtest/bytes_received/config",
    json.dumps(
        base_sensor
        | {
            "name": "Bytes Received",
            "unique_id": "87623514-03b2-45f6-b8ac-1fab3a01f7c4",
            "device_class": "data_size",
            "unit_of_measurement": "MB",
            "value_template": "{{ value_json.bytes_received/1024/1024 }}",
        }
    ),
    retain=True,
)
client.publish(
    "homeassistant/sensor/speedtest/client/config",
    json.dumps(
        base_sensor
        | {
            "name": "Client",
            "unique_id": "bce08b6f-ee16-4bd4-b912-7d2fc470c8b1",
            "json_attributes_topic": "speedtest/status",
            "json_attributes_template": "{{ value_json.client|tojson }}",
            "value_template": "{{ value_json.client.ip }}",
        }
    ),
    retain=True,
)

while True:

    proc = run(cmd, capture_output=True)

    logging.debug("proc: %s", proc)

    message = proc.stdout

    logging.debug("message: %s", message)

    client.publish("speedtest/status", message, retain=True)

    while True:
        x = random.randint(0, 2 * mean)
        y = random.random()
        if y < e ** (-0.5 * ((x - mean) / stdev) ** 2):
            delay = x
            break

    logging.info("Delay: %s", str(timedelta(seconds=delay)))
    time.sleep(delay)
