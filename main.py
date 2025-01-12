import smbus2
import bme280
import time
import paho.mqtt.client as mqtt
import json
import argparse

# Define I2C bus and BME280 address
I2C_BUS = 1
BME280_ADDRESS = 0x76  # Default I2C address for BME280


parser = argparse.ArgumentParser(description="BME280 to MQTT script")
parser.add_argument("--broker", required=True, help="MQTT broker address")
parser.add_argument("--port", type=int, default=1883, help="MQTT broker port")
parser.add_argument("--topic", required=True, help="MQTT topic")
parser.add_argument("--client_id", default="bme280_sensor", help="MQTT client ID")
args = parser.parse_args()


# Assign arguments to variables
MQTT_BROKER = args.broker
MQTT_PORT = args.port
MQTT_TOPIC = args.topic
MQTT_CLIENT_ID = args.client_id

print(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} with client ID {MQTT_CLIENT_ID}")
print(f"Publishing data to topic: {MQTT_TOPIC}")

# Connect to MQTT broker
client = mqtt.Client(MQTT_CLIENT_ID)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Initialize the BME280 sensor
bus = smbus2.SMBus(I2C_BUS)
calibration_params = bme280.load_calibration_params(bus, BME280_ADDRESS)

print("Collecting data. Press Ctrl+C to stop.")

while True:
    # Read sensor data
    data = bme280.sample(bus, BME280_ADDRESS, calibration_params)
    temperature = round(data.temperature, 2)
    humidity = round(data.humidity, 2)
    pressure = round(data.pressure, 2)
        # Create a payload for MQTT
    payload = {
        "name": "BME280 Temperature",
        "state_topic": "sensor/bme280",
        "value_template": "1",
        "unit_of_measurement": "°C",
        "qos": 1
    }



        # Publish to MQTT topic
    client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
    print(f"Published: {payload}")

        # Wait before sending the next data
    time.sleep(1)
