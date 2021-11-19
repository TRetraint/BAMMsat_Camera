###  BAAMSAT CAMERA PAYLOAD MOSFET ###

import RPi.GPIO as GPIO

"""
Class to instanciate the Mosfet features
"""
class Mosfet():
    def __init__(self,Pin): # Constructor of the Class, precise the pin of the Mosfet
        self.Pin = Pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.Pin,1000) # Define the precision of the PWM
        self.pwm.start(0) # Set the PWM to 0
        
    def get_pin(self):
        return self.Pin
    
    def set_pin(self, Pin):
        self.Pin = Pin
    
    def set_pwm(self, DutyCycle): # Change the PWM duty cycle of the Mosfet
        self.pwm.ChangeDutyCycle(DutyCycle)
    
    def stop_pwm(self):
        self.pwm.stop()
    
    def clean_GPIO(self):
        GPIO.cleanup()
    
        