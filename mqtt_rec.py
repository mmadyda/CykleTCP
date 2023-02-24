import paho.mqtt.client as mqtt
import time
mqttTematy = {'MAGAZYN': 'MAGAZYN', 'NASTAWIACZ': 'NASTAWIACZ', 'JAKOSC': 'JAKOSC', 'BRYGADZISTA': 'BRYGADZISTA', 'NARZEDZIOWNIA': 'NARZEDZIOWNIA', 'UTRZYMANIE': 'UTRZYMANIE'}
def on_message(client, userdata, message):
    print("received message: " , str(message.payload.decode("utf-8")))

mqttBroker ="10.0.1.215"

client = mqtt.Client("Marek")
client.connect(mqttBroker, 1883, 60)

client.loop_start()

client.subscribe(mqttTematy['NASTAWIACZ'])
client.on_message=on_message

time.sleep(30)
client.loop_stop()