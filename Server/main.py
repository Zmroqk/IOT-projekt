from datetime import datetime
from pydoc import splitdoc
from paho.mqtt import client as mqtt_client
import database as db

broker = '192.168.56.1'
server_client = 'Server'
port = 1883
server_topic_start = 'terminal/+/+/start'
server_topic_stop = 'terminal/+/+/stop'
server_register_user = 'user/register'

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
      if split_topic.count() == 2 and topic == server_register_user:
         return
      elif split_topic.count() == 4:
         terminal_id = split_topic[1]
         user_id = split_topic[2]

         user = db.session.query(db.User).get(user_id)
         if user is None:
            return

         terminal = db.session.query(db.Terminal).get(terminal_id)
         if terminal is None:
            return

         if topic.find("start"):
            start_message(user, terminal)
         elif topic.find("stop"):
            stop_message(user, terminal)
      else:
         return
      db.session.commit()
   client.subscribe([(server_topic_start, 1), (server_topic_stop, 1), (server_register_user, 1)])
   client.on_message = on_message

def start_message(user: db.User, terminal: db.Terminal):
   if user.balance > 0 and user.active is False and terminal.rentalCount > 0:   
      rental = db.Rental()
      rental.user = user
      user.active = True
      rental.timestamp_start = datetime.now()
      terminal.rentalCount -= 1
      db.session.add(rental)
      client.publish(f'terminal/{terminal.id}/{user.id}/allow')
   else:
      if terminal.rentalCount <= 0:
         client.publish(f'terminal/{terminal.id}/{user.id}/response', payload="Nothing to rent")
      elif user.active is True:
         client.publish(f'terminal/{terminal.id}/{user.id}/response', payload="Already has an active rental")
      else:
         client.publish(f'terminal/{terminal.id}/{user.id}/response', payload="Not enough funds")

def stop_message(user: db.User, terminal: db.Terminal):
   if user.active:
      rental_to_stop: db.Rental = next(rental for rental in user.rentals if rental.timestamp_stop is None)
      rental_to_stop.timestamp_stop = datetime.now()
      user.balance = user.balance - ((rental_to_stop.timestamp_stop - rental_to_stop.timestamp_start).seconds/3600.) * cost_for_an_hour
      terminal.rentalCount += 1
      user.active = False
   else:
      client.publish(f'terminal/{terminal.id}/{user.id}/response', payload="No rental to stop")

client = connect_mqtt()
subscribe_terminals(client)
client.loop_forever()