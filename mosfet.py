import RPi.GPIO as GPIO


class Mosfet():
    def __init__(self,Pin):
        self.Pin = Pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.Pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.Pin,1000)
        self.pwm.start(0)
        
    def get_pin(self):
        return self.Pin
    
    def set_pin(self, Pin):
        self.Pin = Pin
    
    def set_pwm(self, DutyCycle):
        self.pwm.ChangeDutyCycle(DutyCycle)
    
    def stop_pwm(self):
        self.pwm.stop()
    
    def clean_GPIO(self):
        GPIO.cleanup()
    
        