from datetime import datetime
import paho.mqtt.client as mqtt
import time

mqttBroker = '10.0.1.215'

client = mqtt.Client("MASZYNA")
client.connect(mqttBroker)

while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    client.publish("NASTAWIACZ", current_time )
    print("NASTAWIACZ ", current_time )
    time.sleep(1)
