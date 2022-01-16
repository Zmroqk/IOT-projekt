from paho.mqtt import client as mqtt_client;

broker = '192.168.56.1'
server_client = 'Server'
port = 1883
server_topic_start = 'terminal/+/start'
server_topic_stop = 'terminal/+/stop'


def connect_mqtt():
   def on_connect(client, userdata, flags, rc):
      pass
   client = mqtt_client.Client(server_client)
   client.username_pw_set(None)
   client.on_connect = on_connect
   client.connect(broker, port)
   return client

def subscribe_terminals_start(client: mqtt_client.Client):
   def on_message(client, userdata, msg: mqtt_client.MQTTMessage):
      pass
   client.subscribe(server_topic_start)

def subscribe_terminals_stop(client: mqtt_client.Client):
   def on_message(client, userdata, msg: mqtt_client.MQTTMessage):
      pass
   client.subscribe(server_topic_stop)
