from datetime import datetime
from email import message
import ssl
import sys
from paho.mqtt import client as mqtt_client
import database as db
import appController as appCont

session: db.alchemyOrm.Session = db.Session()

broker = '192.168.56.1'
server_client = 'Server'
port = 8883
server_terminal = 'terminal/+'
# server_rerminal_response = 'terminal/+/response'
server_register_user = 'register/+'

cost_for_an_hour = 500

print_logs = False
if '--print-logs' in sys.argv:
   print_logs = True

def connect_mqtt():
   def on_connect(client: mqtt_client.Client, userdata, flags, rc):
      if rc == 5 and print_logs:
         print('MQTT BROKER: Authentication error')
      if client.is_connected() and print_logs:
         print('MQTT BROKER: connected')
   client = mqtt_client.Client(server_client)
   client.username_pw_set('server', 'ServerPassword')
   client.tls_set('../ca.crt', tls_version=ssl.PROTOCOL_TLSv1_2)
   client.tls_insecure_set(True)
   client.on_connect = on_connect
   client.connect(broker, port)
   return client

def subscribe_terminals(client: mqtt_client.Client):
   def on_message(client: mqtt_client.Client, userdata, msg: mqtt_client.MQTTMessage):
      topic: str = msg.topic
      split_topic = topic.split(sep = '/')
      terminal_id = split_topic[1]
      if print_logs:
         print(f'Topic: {topic} Terminal_id: {terminal_id} Message: {msg.payload}')
      if len(split_topic) == 2 and "register" in topic:
         msg_split = str(msg.payload.decode("utf-8")).split('.')
         card_id = msg_split[1]
         user = session.query(db.User).get(msg_split[0])
         users = session.query(db.User).filter(db.User.card_id == card_id).all()
         terminal = session.query(db.RegisterTerminal).get(terminal_id)

         if terminal is None:
            log_to_database(terminal_id, f'Access denied. Terminal with id: {terminal_id} not found')
            session.commit()
            return

         if user is None:
            client.publish(f'register/{terminal_id}/response', 'failure.User does not exist')
            log_to_database(msg.payload, f'User: {msg_split[0]} does not exist')

         else:
            if len(users) != 0:          
               client.publish(f'register/{terminal_id}/response', 'failure.Card already in use')
               log_to_database(msg.payload, f'User: {user.id} cannot be registered with card: {card_id}. Card already in use')
            else:
               user.card_id = card_id
               client.publish(f'register/{terminal_id}/response', f'success.{user.id}.{user.card_id}')
               log_to_database(msg.payload, f'User: {user.id} card: {user.card_id} registered')
      elif len(split_topic) == 2 and "terminal" in topic:  
         card_id = str(msg.payload.decode("utf-8"))
         user = session.query(db.User).filter(db.User.card_id == card_id).first()
         if user is None:
            log_to_database(card_id, f'Access denied. User with card: {card_id} not found')
            session.commit()
            return

         terminal = session.query(db.Terminal).get(terminal_id)
         if terminal is None:
            log_to_database(terminal_id, f'Access denied. Terminal with id: {terminal_id} not found')
            session.commit()
            return

         if user.active is False:
            start_message(user, terminal)
         elif user.active is True:
            stop_message(user, terminal)
      session.commit()
   client.subscribe([(server_terminal, 1), (server_register_user, 1)])
   client.on_message = on_message

def start_message(user: db.User, terminal: db.Terminal):
   if user.balance > 0 and terminal.rentalCount > 0:   
      rental = db.Rental()
      rental.user = user
      user.active = True
      rental.timestamp_start = datetime.now()
      terminal.rentalCount -= 1
      session.add(rental)
      client.publish(f'terminal/{terminal.id}/response', 'allow.start')
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
   client.publish(f'terminal/{terminal.id}/response', 'allow.stop')
   log_to_database(user.card_id, f'Rental for card: {user.card_id} stoped')

def log_to_database(card_id: str, logmsg: str):
   log = db.Log()
   log.card_id = card_id
   log.timestamp = datetime.now()
   log.log = logmsg
   if print_logs:
      print(f'{log.timestamp}: {log.log}')
   session.add(log)

client = connect_mqtt()
subscribe_terminals(client)
client.loop_start()
appCont.startApp()