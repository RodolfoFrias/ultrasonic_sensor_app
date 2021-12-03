import machine, time
from machine import Pin
from time import sleep
import urequests
import network
import json
import gc
import os

class Config:
    SSID='ARRIS-9FE2' # SSID of your WiFi network
    PASSWORD='FBD7AD20BDAE434300' # Password of your WiFi network
    API_URL='http://192.168.0.16:3000/api/iot/notification' # URL of your API

class Logger:
    def info(self, msg):
        print("INFO: ", msg)

    def error(self, msg):
        print("ERROR: ", msg)

    def debug(self, msg):
        print("DEBUG: ", msg)

    def warning(self, msg):
        print("WARNING: ", msg)

logger = Logger()
config = Config()

class HCSR04:
    """
    Driver to use the untrasonic sensor HC-SR04.
    The sensor range is between 2cm and 4m.
    The timeouts received listening to echo pin are converted to OSError('Out of range')
    """
    # echo_timeout_us is based in chip range limit (400cm)
    def __init__(self, trigger_pin, echo_pin, echo_timeout_us=500*2*30):
        """
        trigger_pin: Output pin to send pulses
        echo_pin: Readonly pin to measure the distance. The pin should be protected with 1k resistor
        echo_timeout_us: Timeout in microseconds to listen to echo pin.
        By default is based in sensor limit range (4m)
        """
        self.echo_timeout_us = echo_timeout_us
        # Init trigger pin (out)
        self.trigger = Pin(trigger_pin, mode=Pin.OUT, pull=None)
        self.trigger.value(0)

        # Init echo pin (in)
        self.echo = Pin(echo_pin, mode=Pin.IN, pull=None)

    def _send_pulse_and_wait(self):
        """
        Send the pulse to trigger and listen on echo pin.
        We use the method `machine.time_pulse_us()` to get the microseconds until the echo is received.
        """
        self.trigger.value(0) # Stabilize the sensor
        time.sleep_us(5)
        self.trigger.value(1)
        # Send a 10us pulse.
        time.sleep_us(10)
        self.trigger.value(0)
        try:
            pulse_time = machine.time_pulse_us(self.echo, 1, self.echo_timeout_us)
            return pulse_time
        except OSError as ex:
            if ex.args[0] == 110: # 110 = ETIMEDOUT
                raise OSError('Out of range')
            raise ex

    def distance_mm(self):
        """
        Get the distance in milimeters without floating point operations.
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.34320 mm/us that is 1mm each 2.91us
        # pulse_time // 2 // 2.91 -> pulse_time // 5.82 -> pulse_time * 100 // 582
        mm = pulse_time * 100 // 582
        return mm

    def distance_cm(self):
        """
        Get the distance in centimeters with floating point operations.
        It returns a float
        """
        pulse_time = self._send_pulse_and_wait()

        # To calculate the distance we get the pulse_time and divide it by 2
        # (the pulse walk the distance twice) and by 29.1 becasue
        # the sound speed on air (343.2 m/s), that It's equivalent to
        # 0.034320 cm/us that is 1cm each 29.1us
        cms = (pulse_time / 2) / 29.1
        return cms


class WIFI:
    """
    Initialize the integrated WIFI module
    """
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password


    def connect(self):
        """Connect to the WIFI network"""
        wlan = network.WLAN(network.STA_IF)
        if not wlan.isconnected():
            wlan.active(True)
            wlan.connect(self.ssid, self.password)
            timeout = time.time ()
            logger.info('Connecting to WIFI...')
            while not wlan.isconnected():
                if (time.ticks_diff (time.time (), timeout) > 60):
                    return False
            logger.debug('Network config: ' + wlan.ifconfig())

        return wlan

class App:
    def __init__(self):
        self.sensor = HCSR04(trigger_pin=12, echo_pin=14, echo_timeout_us=10000)
        self.wifi = WIFI(config.SSID , config.PASSWORD).connect()

    def run_again(self):
        logger.debug('Running again...')
        self.run()

    def run(self):
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        if self.wifi:
            logger.debug('Connected to WIFI')
            while True:

                if not self.wifi.isconnected():
                    machine.reset()

                distance = self.sensor.distance_cm()

                if distance <= 5 and distance > 0:
                    logger.info('Sending with distance \n')
                    logger.info(distance)
                    success = self.sendRequest(distance)
                    if success:
                        break

                logger.info('Distance:' + str(distance) + 'cm')
                sleep(1)
            sleep(60) # 60 seconds to wait until the app runs again
            self.run_again()

        else:
            logger.warn('No wifi connection')

    def sendRequest(self, distance):
        """Send a request to the server"""
        logger.debug('Sending request...')
        api_url = config.API_URL
#       message = 'Distance around : ' + str(distance)
        message = 'El agua ya we'
        payload = {'message': message}

        try:
            logger.debug(payload)
            headers = {'Content-Type':'application/json', 'Accept': 'application/json'}
            data = (json.dumps(payload)).encode()
            response = urequests.post(api_url, data=data, headers=headers)
            logger.debug(response.json())
            return True
        except Exception as e:
            logger.error(e)
            return False

if __name__ == '__main__':
    app = App()
    app.run()
