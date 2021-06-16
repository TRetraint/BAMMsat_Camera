from smbus import SMBus

class Temperature_Sensor():
    def __init__(self,Address):
        self.Address = Address
    
    bus = SMBus(1)
       
    def get_address(self):
        return Address
       
    def set_address(self,Address):
        self.Address = Address
        
    def word_To_LSB_MSB(self,word):
        return word[0:8], word[12:16]
    
    def get_temp(self):
        x = format(self.bus.read_word_data(self.Address,0x05),'016b')
        LSB, MSB = self.word_To_LSB_MSB(x)
        temp = float(int(MSB+LSB,2))/16
        if temp > 150:
            temp = temp - 256
        return temp