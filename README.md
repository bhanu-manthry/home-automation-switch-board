# Smart Switch Board for Home Automation

Smart Switch Board is written in python and runs on RaspberryPi.
Commands to control the devices are received on MQTT topic to which this program subscribes.
Devices are controlled by pressing the buttons on the matrix keypad and based on the messages received on the subscribed mqtt topic. 

## Usage
Clone this repo and and put your MQTT details in main.py

```python
# put the addres of the mqtt borker, exmaple: 49.206.52.201
broker = ""

# Messages from the app are received on this topic, example: home/bedroom
self_topic = ""

# Topic to which this program publishes tha status and acknowledgement messages, example: phone/remote
remote_topic = ""

# Location of the log file name, exmaple: /home/pi/switch_board/switch_board.log
log_file_name = ""
```