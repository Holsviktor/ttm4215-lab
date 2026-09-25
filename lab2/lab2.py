import paho.mqtt.client as mqtt

import datetime
from random import random
from time import sleep
from threading import Thread, Lock

from sense_hat import SenseHat

#############################################################################################################################
URL = "mqtt20.iik.ntnu.no"
MQTT_PORT = 1883
HUMIDITY_SUBSCRIBER_TOPIC = "ttm4115/group1/+/humidity"
HUMIDITY_PUBLISH_TOPIC = lambda id : f"ttm4115/group1/{id}/humidity"

STATUS_SUBSCRIBER_TOPIC = "ttm4115/group1/+/status"
STATUS_PUBLISH_TOPIC = lambda id : f"ttm4115/group1/{id}/status"
FIX_TOPIC = "ttm4115/group1/actions/fix"
POLL_TOPIC = "ttm4115/group1/actions/poll"
SYSTEM_STATUS_TOPIC = "ttm4115/group1/status"


class MQTT_Connection:
    def __init__(self,id, connect_callback=None, message_callback=None):
        self.broker = URL
        self.port = MQTT_PORT
        self.id = id
        self.status = STATUS_CONNECTING
        self.humidity_topic = HUMIDITY_PUBLISH_TOPIC(id)
        self.status_topic = STATUS_PUBLISH_TOPIC(id)
        if id is None:
            self.humidity_topic = None
        self.connections = list()

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

        if message_callback != None:
            self.client.on_message = message_callback
        if connect_callback != None:
            self.client.on_connect = connect_callback
    def connect(self):
        return self.client.connect(self.broker, self.port, 60) == 0

#############################################################################################################################
## Constants
STATUS_CONNECTING = 40
STATUS_OPERATIONAL = 63
STATUS_DISCONNECTED = 86
STATUS_SENSOR_FAIL = 109

NETWORK_FAIL_PROBABILITY = 0.1
SENSOR_FAIL_PROBABILITY = 0.1
REPAIR_RATE = 0.5

TIMEOUT = 5

def humidity_sensor(id): # Sensor Thread
    mqtt_connection = None
    def random_failure_maybe(mqtt_connection):
        if mqtt_connection.status != STATUS_OPERATIONAL:
            return
        random_num = random()
        if random_num < SENSOR_FAIL_PROBABILITY:
            mqtt_connection.status = STATUS_SENSOR_FAIL
            print(f'{id} broke its sensor!')
        elif random_num >= SENSOR_FAIL_PROBABILITY and random_num < SENSOR_FAIL_PROBABILITY + NETWORK_FAIL_PROBABILITY:
            mqtt_connection.status = STATUS_DISCONNECTED
            print(f'{id} am become disconnected.')
    
    def maybe_reconnect(mqtt_connection):
            random_repair = random()
            if random_repair < REPAIR_RATE: 
                print(f'{id}, has reconnected.')
                mqtt_connection.status = STATUS_OPERATIONAL
                return True
            return False

    def connected_callback(client, userdata, flags, reason_code, properties):
        subscribe_status = client.subscribe(FIX_TOPIC)
        if subscribe_status == 1:
            print(f"{id} could not subscribe to fix: {subscribe_status}")

    def fix_sensor(client, userdata, m):
        if m.topic == FIX_TOPIC and mqtt_connection.status == STATUS_SENSOR_FAIL:
            print(f"{id} is fixed") 
            mqtt_connection.status = STATUS_OPERATIONAL
            show_status(id, mqtt_connection.status)

    print(f"I am a humidity publisher with id {id}")
    sense = SenseHat()
    mqtt_connection = MQTT_Connection(id, connect_callback=connected_callback, message_callback=fix_sensor)
    mqtt_connection.client.loop_start()

    while True:
        random_failure_maybe(mqtt_connection)
        show_status(id, mqtt_connection.status)
        mqtt_connection.client.publish(mqtt_connection.status_topic, mqtt_connection.status)
        
        # Operational
        if mqtt_connection.status == STATUS_OPERATIONAL:
            humidity = round(sense.get_humidity())
            mqtt_connection.client.publish(mqtt_connection.humidity_topic, f'{{ "humidity" : {humidity:.2f} }}')

        # Disconnected
        elif mqtt_connection.status == STATUS_DISCONNECTED:
            if maybe_reconnect(mqtt_connection):
                humidity = round(sense.get_humidity())
                mqtt_connection.client.publish(mqtt_connection.humidity_topic, f'{{ "humidity" : {humidity:.2f} }}')
                
        # Sensor failed
        elif mqtt_connection.status == STATUS_SENSOR_FAIL:
            # This state is transitioned out of through a message to FIX_TOPIC
            #   It would be more readable if this node read messages from a buffer
            #       rather than through a callback.
            bogus_data = 100*random()
            msg_info = (
                mqtt_connection
                .client
                .publish(
                    mqtt_connection.humidity_topic, 
                    f'{{ "humidity" : {bogus_data:.2f} }}'
                )
            )

        # Connecting
        elif mqtt_connection.status == STATUS_CONNECTING:
            if mqtt_connection.connect():
                mqtt_connection.status = STATUS_OPERATIONAL 
                print(f"Node {id} connection success")
                continue
            else:
                print("failure")
                mqtt_connection.status = STATUS_DISCONNECTED
            
        sleep(TIMEOUT)
#############################################################################################################################
def fixer_thread(): # This thread emulates surveillance test
    mqtt_connection = MQTT_Connection(None)
    mqtt_connection.connect()
    while (True):
        error = mqtt_connection.client.publish(FIX_TOPIC, 'You are now fixed!')
        sleep(10)

def poller_thread(): # This thread emulates surveillance test
    mqtt_connection = MQTT_Connection(None)
    mqtt_connection.connect()
    while (True):
        error = mqtt_connection.client.publish(POLL_TOPIC, 'Its time to print')
        sleep(5)
#############################################################################################################################
_dict_lock = Lock()

HEALTHY_STATE = "SAFE"
SAFE_FAILURE = "SAFE_FAILURE"
UNSAFE_FAILURE = "UNSAFE_FAILURE"

current_state = ""
def aggregator(): # Reads messages and contains the final 2oo3/2oo4 aggregation logic
    sensor_readings = dict()
    def connected_callback(client, userdata, flags, reason_code, properties):
        print("I am become connected, connector of worlds.")
        subscribe_error = client.subscribe(HUMIDITY_SUBSCRIBER_TOPIC)
        subscribe_error = client.subscribe(POLL_TOPIC)
        if subscribe_error == 1:
            print(f"Aggregator failed to subscribe to humidity topic: {subscribe_error}")

    def message_received_callback(client, userdata, m):
        #print(f"I received a message {m.payload} from {m.topic}")
        with _dict_lock:
            if m.topic.split('/')[-1] == "humidity":
                sensor_readings[m.topic] =  m.payload
                print(f'Added reading: {sensor_readings[m.topic]}')
                # set the correct humidity reading from that sensor
            elif m.topic == POLL_TOPIC:
                #non_disconnected_count = len([v for v in sensor_readings.values() if not v is Node])
                readings = list(sensor_readings.values())
                most_common_reading = max(set(readings), key=readings.count)
                working_count = readings.count(most_common_reading)
                if working_count >= 3:
                    current_state = HEALTHY_STATE
                elif working_count == 2:
                    current_state = SAFE_FAILURE
                else:
                    current_state = UNSAFE_FAILURE

                client.publish(SYSTEM_STATUS_TOPIC, current_state)

                print("number of working sensors: ", working_count)
                print("Current state: ", current_state)
                if current_state != UNSAFE_FAILURE:
                    print("Humidity: ", most_common_reading)
                else:
                    print("Could not get a humidity reading.")
                with open('state-history', 'a') as f:
                    f.write(f"{current_state}\n")

                # Empty the dictionary
                #   Used for timeouts
                for topic in sensor_readings.copy().keys():
                    reading = sensor_readings[topic]
                    if reading is None:
                        continue

                    #print(f"{topic}:{reading}")
                    sensor_readings[topic] = None


    with open('state-history', 'w') as f:
        f.write('')
    mqtt_connection = MQTT_Connection(
        '+', 
        connect_callback=connected_callback,
        message_callback=message_received_callback
    )
    mqtt_connection.connect()
    mqtt_connection.client.loop_forever()
#############################################################################################################################
_pixel_buffer = [(0, 0, 0)] * 64  
_buffer_lock = Lock()
colors = {
    STATUS_CONNECTING: (255, 255, 255),   # White
    STATUS_OPERATIONAL: (0, 255, 0),      # Green
    STATUS_DISCONNECTED: (255, 255, 0),   # Yellow
    STATUS_SENSOR_FAIL: (255, 0, 0),      # Red
}
def show_status(i, k):
    assert(k in colors.keys())
    sense = SenseHat()
    
    color = [c//2 for c in colors.get(k, None)]

    column = i-1
    with _buffer_lock:
        for row in range(8):
            idx = row * 8 + 2*column
            _pixel_buffer[idx] = color
            idx = row * 8 + 2*column + 1
            _pixel_buffer[idx] = color
    sense.set_pixels(_pixel_buffer)
#############################################################################################################################
if __name__ == '__main__':
    for id in range (3):
        # Start all threads and then just wait forever :)
        humidity_sensor_thread = Thread(target=humidity_sensor, args=[id])
        humidity_sensor_thread.start()
        sleep(TIMEOUT/4)

    fix_thread = Thread(target=fixer_thread)
    fix_thread.start()
    poll_thread = Thread(target=poller_thread)
    poll_thread.start()

    subscriber_thread = Thread(target=aggregator)
    subscriber_thread.start()

    input()
