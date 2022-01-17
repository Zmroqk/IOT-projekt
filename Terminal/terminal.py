import paho.mqtt.client as mqtt

terminal_id = 'T0'
broker = '192.168.56.1'

client = mqtt.Client()

# Send to server on terminal/<<terminal_id>>
def send_message(card_id):
    client.publish(f'terminal/{terminal_id}', card_id)

def interface():
    should_run = True
    while should_run:
        card_id = input('State card id: ')
        send_message(card_id)
        print(card_id)

def process_message(client, userdata, message):
    pass

# Receiver from server terminal/<<terminal_id>>/response 
def connect_to_broker():
    client.connect(broker)
    client.on_message = process_message
    client.loop_start()
    client.subscribe(f'terminal/{terminal_id}/response')


def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()

def run_sender():
    interface()

    connect_to_broker()

    disconnect_from_broker()

if __name__ == "__main__":
    run_sender()


