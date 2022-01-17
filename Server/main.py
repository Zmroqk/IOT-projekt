import csv
from datetime import datetime
from paho.mqtt import client as mqtt_client
import database as db

broker = '192.168.56.1'
server_client = 'Server'
port = 1883
server_terminal = 'terminal/+'
# server_rerminal_response = 'terminal/+/response'
server_register_user = 'user/+/register'

cost_for_an_hour = 500

def connect_mqtt():
   def on_connect(client: mqtt_client.Client, userdata, flags, rc):
      if rc == 5:
         print('MQTT BROKER: Authentication error')
   client = mqtt_client.Client(server_client)
   client.username_pw_set('server', 'ServerPassword')
   client.on_connect = on_connect
   client.connect(broker, port)
   return client

def subscribe_terminals(client: mqtt_client.Client):
   def on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
      topic: str = msg.topic
      split_topic = topic.split(sep = '/')
      print(topic)
      print(msg.payload)
      if len(split_topic) == 3 and topic == server_register_user:
         user = db.session.query(db.User).get(split_topic[1])
         user.card_id = msg.payload
         log_to_database(msg.payload, f'User: {user.id} card: {user.card_id} registered')
      elif len(split_topic) == 2:
         terminal_id = split_topic[1]
         card_id = split_topic[2]

         user = db.session.query(db.User).filter(db.User.card_id == card_id).first()
         if user is None:
            log_to_database(card_id, f'Access denied. User with card: {card_id} not found')
            db.session.commit()
            return

         terminal = db.session.query(db.Terminal).get(terminal_id)
         if terminal is None:
            log_to_database(terminal_id, f'Access denied. Terminal with id: {terminal_id} not found')
            db.session.commit()
            return

         if user.active is False:
            start_message(user, terminal)
         elif user.active is True:
            stop_message(user, terminal)
      db.session.commit()
   client.subscribe([(server_terminal, 1), (server_register_user, 1)])
   client.on_message = on_message

def start_message(user: db.User, terminal: db.Terminal):
   if user.balance > 0 and terminal.rentalCount > 0:   
      rental = db.Rental()
      rental.user = user
      user.active = True
      rental.timestamp_start = datetime.now()
      terminal.rentalCount -= 1
      db.session.add(rental)
      client.publish(f'terminal/{terminal.id}/response', 'allow')
      log_to_database(user.card_id, f'Rental for card: {user.card_id} started')
   else:
      if terminal.rentalCount <= 0:
         client.publish(f'terminal/{terminal.id}/response', payload="denied.Nothing to rent")
         log_to_database(user.card_id, f'Rental for card: {user.card_id} denied. Nothing to rent on terminal: {terminal.id}')
      else:
         client.publish(f'terminal/{terminal.id}/response', payload="denied.Not enough funds")
         log_to_database(user.card_id, f'Rental for card: {user.card_id} denied. Not enough funds')

def stop_message(user: db.User, terminal: db.Terminal):
   rental_to_stop: db.Rental = next(rental for rental in user.rentals if rental.timestamp_stop is None)
   rental_to_stop.timestamp_stop = datetime.now()
   user.balance = user.balance - ((rental_to_stop.timestamp_stop - rental_to_stop.timestamp_start).seconds/3600.) * cost_for_an_hour
   terminal.rentalCount += 1
   user.active = False
   log_to_database(user.card_id, f'Rental for card: {user.card_id} stoped')

def log_to_database(card_id: str, logmsg: str):
   log = db.Log()
   log.card_id = card_id
   log.timestamp = datetime.now()
   log.log = logmsg
   db.session.add(log)

def print_logs_to_csv():
   with open('logs.csv', 'w', newline='') as csvfile:
      writer = csv.writer(csvfile, dialect='excel')
      logs = db.session.query(db.Log).all()
      writer.writerow(['id', 'card_id', 'timestamp', 'log'])
      for log in logs:
         writer.writerow([log.id, log.card_id, log.timestamp, log.log])

client = connect_mqtt()
subscribe_terminals(client)
client.loop_start()
while(True):
   cmd = input('Podaj komende: ')
   if cmd == 'print-logs':
     print_logs_to_csv()
