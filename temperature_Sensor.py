###  BAAMSAT CAMERA PAYLOAD TEMPERATURE SENSOR ###

from smbus import SMBus

"""
Class to instanciate the temperature sensor features
"""
class Temperature_Sensor():
    def __init__(self,Address): # Constructor of the class, set the I2C address of the Sensor
        self.Address = Address
    
    bus = SMBus(1) # Bus Communication protocol
       
    def get_address(self):
        return self.Address
       
    def set_address(self,Address):
        self.Address = Address
        
    def word_To_LSB_MSB(self,word): # Extract the information from the sensors values 
        return word[0:8], word[12:16]
    
    def get_temp(self): # Convert the bytes from the sensors into °C values
        x = format(self.bus.read_word_data(self.Address,0x05),'016b')
        LSB, MSB = self.word_To_LSB_MSB(x)
        temp = float(int(MSB+LSB,2))/16
        if temp > 150: # statement to deal with negative values 
            temp = temp - 256
        return temp