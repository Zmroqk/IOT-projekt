import paho.mqtt.client as mqtt

terminal_id = 'RT0'
broker = '192.168.56.1'

client = mqtt.Client()

# Send to server on register/<<terminal_id>>
def send_message(user_id, card_id):
    """Message payload format: <<user_id>>.<<card_id>>"""
    client.publish(f'register/{terminal_id}', f'{user_id}.{card_id}')

def interface():
    should_run = True
    while should_run:
        card_id = input('State card id: ')
        send_message(card_id)
        print(card_id)

def process_message(client, userdata, message):
    """Message payload format: (1) success.<<user_id>>.<<card_id>> (2) failure.<<reason>>"""
    message_decoded = (str(message.payload.decode("utf-8"))).split(".")

    try:
        if message_decoded[0].lower() == 'failure':
            print('Operation denied: ' + message_decoded[1])
        elif message_decoded[0].lower() == 'success':
            print(f'Card {message_decoded[1]} successfully added for user {message_decoded[2]}.')
    except IndexError:
        print('Illegal server response')
        

# Receiver from server register/<<terminal_id>>/response
def connect_to_broker():
    client.connect(broker)
    client.on_message = process_message
    client.loop_start()
    client.subscribe(f'register/{terminal_id}/response')


def disconnect_from_broker():
    client.loop_stop()
    client.disconnect()

def run_sender():
    interface()

    connect_to_broker()

    disconnect_from_broker()

if __name__ == "__main__":
    run_sender()


