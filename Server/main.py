from datetime import datetime
from paho.mqtt import client as mqtt_client
import database as db

broker = '192.168.56.1'
server_client = 'Server'
port = 1883
server_topic_start = 'terminal/+/+/start'
server_topic_stop = 'terminal/+/+/stop'

cost_for_an_hour = 500

def connect_mqtt():
   def on_connect(client, userdata, flags, rc):
      pass
   client = mqtt_client.Client(server_client)
   client.username_pw_set(None)
   client.on_connect = on_connect
   client.connect(broker, port)
   return client

def subscribe_terminals(client: mqtt_client.Client):
   def on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
      topic: str = msg.topic
      split_topic = topic.split(sep = '/')
      if split_topic.count() != 4:
         return
      terminal_id = split_topic[1]
      user_id = split_topic[2]

      user = db.session.query(db.User).get(user_id)
      if user is None:
         return

      terminal = db.session.query(db.Terminal).get(terminal_id)
      if terminal is None:
         return

      if topic.find("start"):
         if user.balance > 0 and user.active is False:   
            rental = db.Rental()
            rental.user = user
            user.active = True
            rental.timestamp_start = datetime.now()
            client.publish(f'terminal/{terminal_id}/{user_id}/allow')
         else:
            client.publish(f'terminal/{terminal_id}/{user_id}/response', payload="Not enough funds")
      elif topic.find("stop"):
         if user.active:
            rental_to_stop: db.Rental = next(rental for rental in user.rentals if rental.timestamp_stop is None)
            rental_to_stop.timestamp_stop = datetime.now()
            user.balance = user.balance - ((rental_to_stop.timestamp_stop - rental_to_stop.timestamp_start).seconds/3600.) * cost_for_an_hour
            user.active = False
         else:
            client.publish(f'terminal/{terminal_id}/{user_id}/response', payload="No rental to stop")
   client.subscribe([(server_topic_start, 1), (server_topic_stop, 1)])
   client.on_message = on_message

client = connect_mqtt()
subscribe_terminals(client)
client.loop_forever()