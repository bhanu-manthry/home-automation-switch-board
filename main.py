import paho.mqtt.client as mqtt
import time
import RPi.GPIO as GPIO
import urllib2
import logging
from keypad import Keypad
import multiprocessing
import json

# put the addres of the mqtt borker, exmaple: 49.206.52.201
broker = ""

# Messages from the app are received on this topic, example: home/bedroom
self_topic = ""

# Topic to which this program publishes tha status and acknowledgement messages, example: phone/remote
remote_topic = ""

# Location of the log file name, exmaple: /home/pi/switch_board/switch_board.log
log_file_name = ""

logging.basicConfig(filename = log_file_name,
        level = logging.DEBUG)
logger = logging.getLogger()

logger.info("Script started")

client = None

# change this based on the relay connections
relays = {
    1: 4,
    2: 17,
    3: 27,
    4: 22,
    5: 14,
    6: 15,
    7: 18,
    8: 23
}

relays_status = {
    1: False,
    2: False,
    3: False,
    4: False,
    5: False,
    6: False,
    7: False,
    8: False
}

GPIO.setmode(GPIO.BCM) # bcm numbering

for i in range(1, 9):
    GPIO.setup(relays[i], GPIO.OUT)
    GPIO.output(relays[i], GPIO.HIGH)

def internet_on():
    try:
        urllib2.urlopen('https://google.co.in', timeout=1)
        return True
    except urllib2.URLError as err:
        return False


def on_connect(self, client, userdata, rc):
    logger.info("Connected to broker")
    print("Connected with result code "+str(rc))
    self.subscribe(self_topic)


def on_message(client, userdata, msg):
    msg_str = str(msg.payload)
    print("Message arrived: " + msg_str)
    message_handler(msg_str)

def on_log(client, userdata, level, buf):
    print("log: " + buf)

def toggle_switch(msg):
    try:
        n = int(msg)
        if (relays_status[n] == False):
            GPIO.output(relays[n],GPIO.LOW)
            relays_status[n] = True
        else:
            GPIO.output(relays[n],GPIO.HIGH)
            relays_status[n] = False

        if (client == None):
            logging.debug('Mqtt client is not connected to broker')
            print('mqtt client is not connected to broker')
        else:
            publish_msg_str = 'ACK_SET ~ ' + json.dumps({'key': n, 'val': relays_status[n]})
            print('publishing message -> ' + publish_msg_str)
            client.publish(remote_topic, publish_msg_str)
    except Exception as e:
        print("Exception occurred while switching relay after key press")
        print(e)

def message_handler(msg):
    if (msg == 'GET_STATUS'):
        if (client == None):
            print('mqtt client is None')
            return

        publish_msg_str = 'STATUS ~ ' + json.dumps(relays_status)
        print('publishing status message')
        client.publish(remote_topic, publish_msg_str)

    if (msg.startswith('SET')):
        try:
            received_status = msg.split('~')[1].strip()
            received_json = json.loads(received_status)

            key = received_json["key"]
            val = received_json["val"]

            if (val == True):
                GPIO.output(relays[key], GPIO.LOW)
                relays_status[key] = True
            else:
                GPIO.output(relays[key],GPIO.HIGH)
                relays_status[key] = False

            if (client == None):
                logging.debug('Mqtt client is not connected to broker')
                print('mqtt client is not connected to broker')
            else:
                publish_msg_str = 'ACK_SET ~ ' + json.dumps({'key': key, 'val': relays_status[key]})
                client.publish(remote_topic, publish_msg_str)
        except Exception as e:
            print("Exception occurred while switching relay")
            print (e)


def check_relays():
    while True:
        for i in range(1, 9):
            GPIO.output(relays[i], GPIO.LOW)
            time.sleep(2)
            GPIO.output(relays[i], GPIO.HIGH)
            time.sleep(2)

def listenForKeypadEvents():
    kp = Keypad()
    digit = None

    try:
        while True:
            if digit == None:
                digit = kp.getKey() # blocking call
            else:
                print digit
                print("key pressed: " + digit)
                logger.info("Key pressed: " + digit)
                toggle_switch(digit)
                time.sleep(.4)
                digit = None
    except KeyboardInterrupt:
        print("Keyboard interrupt")
        GPIO.cleanup()

def mqttWorker():
    while True:
        if not internet_on():
            print("Cannot connect to internet")
            logger.info("Cannot connect to internet, waiting for internet connection...")
            time.sleep(1)
            continue

        print("Connecting to mqtt broker...")
        logger.info("Connecting to mqtt broker...")
        client.connect(broker, 1883, 60)
        client.loop_forever()
        break

if __name__ == '__main__':
    client = mqtt.Client('bhanu_switch_board')
    #client.username_pw_set(auth['username'], auth['password'])
    client.on_connect = on_connect
    client.on_message = on_message

    keypadThread = multiprocessing.Process(target=listenForKeypadEvents)
    keypadThread.daemon = True

    mqttWorkerThread = multiprocessing.Process(target=mqttWorker)
    mqttWorkerThread.daemon = True

    mqttWorkerThread.start()
    keypadThread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Keyboard interrupt, Program forcibly colsed by user!")
        GPIO.cleanup()
