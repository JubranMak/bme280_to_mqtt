import smbus2
import bme280
import time
from paho.mqtt import client as mqtt_client
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
client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, MQTT_CLIENT_ID)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Initialize the BME280 sensor
bus = smbus2.SMBus(I2C_BUS)
calibration_params = bme280.load_calibration_params(bus, BME280_ADDRESS)

print("Collecting data. Press Ctrl+C to stop.")

# Define the MQTT sensor configurations for Home Assistant discovery
sensor_configs = {
    "temperature": {
        "name": "BME280 Temperature",
        "state_topic": f"{MQTT_TOPIC}/state",
        "value_template": "{{ value_json.temperature }}",
        "unit_of_measurement": "°C",
        "device_class": "temperature",
        "unique_id": "bme280_temperature",
        "qos": 1,
    },
    "humidity": {
        "name": "BME280 Humidity",
        "state_topic": f"{MQTT_TOPIC}/state",
        "value_template": "{{ value_json.humidity }}",
        "unit_of_measurement": "%",
        "device_class": "humidity",
        "unique_id": "bme280_humidity",
        "qos": 1,
    },
    "pressure": {
        "name": "BME280 Pressure",
        "state_topic": f"{MQTT_TOPIC}/state",
        "value_template": "{{ value_json.pressure }}",
        "unit_of_measurement": "hPa",
        "device_class": "pressure",
        "unique_id": "bme280_pressure",
        "qos": 1,
    },
}

# Publish the sensor configurations for Home Assistant discovery
for sensor, config in sensor_configs.items():
    config_topic = f"{MQTT_TOPIC}_{sensor}/config"
    client.publish(config_topic, json.dumps(config), qos=1, retain=True)

# Keep the client loop running to handle connections and messages
client.loop_start()

try:
    while True:
        # Read sensor data
        data = bme280.sample(bus, BME280_ADDRESS, calibration_params)
        temperature = round(data.temperature, 2)
        humidity = round(data.humidity, 2)
        pressure = round(data.pressure, 2)

        # Create a payload for MQTT with actual sensor values
        payload = {
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
        }

        # Publish the sensor data to the topic
        client.publish(f"{MQTT_TOPIC}/state", json.dumps(payload), qos=1, retain=False)

        # Wait for a few seconds before reading data again
        time.sleep(10)  # Adjust the interval as needed
except KeyboardInterrupt:
    print("Stopping...")
finally:
    client.loop_stop()
    client.disconnect()