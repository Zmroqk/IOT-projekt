import ssl
import sys
import paho.mqtt.client as mqtt

terminal_id = sys.argv[1]
broker = '192.168.56.1'

client = mqtt.Client('T' + sys.argv[1])

# Send to server on terminal/<<terminal_id>>
def send_message(card_id):
    client.publish(f'terminal/{terminal_id}', card_id)

def interface():
    should_run = True
    while should_run:
        card_id = input('State card id: ')
        send_message(card_id)

def process_message(client, userdata, message):
    """Message payload format: (1) allow.<<rent_status>> (2) denied.<<reason>>"""
    message_decoded = (str(message.payload.decode("utf-8"))).split(".")

    try:
        if message_decoded[0].lower() == 'denied':
            print('Operation denied: ' + message_decoded[1])
        elif message_decoded[0].lower() == 'allow':
            print('Operation allowed: ' + message_decoded[1])
    except IndexError:
        print('Illegal server response')
        

# Receiver from server terminal/<<terminal_id>>/response 
def connect_to_broker():
    client.username_pw_set('server', 'ServerPassword')
    client.tls_set('../ca.crt', tls_version=ssl.PROTOCOL_TLSv1_2)
    client.tls_insecure_set(True)

    client.connect(broker, 8883)
    client.on_message = process_message
    client.loop_start()
    client.subscribe(f'terminal/{terminal_id}/response')


def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()

def run_sender():
   connect_to_broker()
   interface()
   disconnect_from_broker()

if __name__ == "__main__":
    run_sender()


