import socket
import logging
import queue
import csv
import threading
from datetime import datetime
from time import sleep
from multiprocessing import Process
from gpiozero import CPUTemperature
from temperature_Sensor import Temperature_Sensor
from mosfet import Mosfet
from camera import Camera
#from current_sensor import save_current

class Log:
    def __init__(self,filename):
        logging.basicConfig(filename=filename, format='[%(levelname)s] %(asctime)s: %(message)s',level=logging.INFO)
        
class Server:
    def __init__(self,Host,Port):
        self.Host = Host
        self.Port = Port
        
    def get_Host(self):
        return self.Host
    
    def get_Port(self):
        return self.Port
    
    def set_Host(self,Host):
        self.Host = Host
    
    def set_Port(self,Port):
        self.Port = Port
    
    def set_temp_sensor(self,temp_sensor):
        self.temp_sensor = temp_sensor
    
    def set_mosfets(self,mosfets):
        self.mosfet_list = mosfets
    
    def set_interval_temp(self,interval):
        self.interval_temp = interval
    
    def set_interval_temp(self,interval):
        self.interval_mosfet = interval
    
    def set_camera(self,cam):
        self.camera = cam
        
    
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection = 0
    process_save_temp = 0
    in_process_save_temp = False
    in_connection = False
    temp_sensor = []
    interval_temp = 2
    interval_mosfet = 2
    mosfet_list = []
    process_auto_heat = 0
    in_process_auto_heat = False
    camera = 0
    process_record = 0
    in_process_record = False
    process_currrent = 0
    
    def __setup_connection(self):
        try:
            self.socket.listen(1)
            print("Waiting for connection")
            logging.info("Waiting for connection")
            conn, addr = self.socket.accept()
            print("Connected with: {}".format(addr))
            logging.info("Connected with: {}".format(addr))
            return conn
        except:
            print("No connection found")
            logging.error("No connection found")
        
    def save_current(self,filename):
        with open(filename,mode="a") as csv_file:
                csv_file.write("{0},{1},{2},{3}\n".format("Date","Tension","Intensite","Puissance"))
                while True:
                    current = get_curent()
                    csv_file.write("{0},{1},{2},{3}\n".format(str(datetime.now()),str(current[0]),str(current[1]),str(current[2])))
                    csv_file.flush()
                    sleep(2)
    
    def establish_connection(self):
        try:
            print("Connection on Port {} Open".format(self.Port))
            logging.info("Connection on Port {} Open".format(self.Port))
            self.socket.bind((self.Host,self.Port))
            self.connection = self.__setup_connection()
            self.in_connection = True
        except:
            print("Can't open connection")
            logging.error("Can't open connection")

    
    def __command_library(self,command,data):
        reply = ""
        if command == 'REPEAT':
            reply = data[1]
        elif command == 'LOGOUT':
            print('System logout')
            reply = 'Server logging out'
            
        elif command == 'SAVE_TEMP':
            self.process_save_temp = Process(target=self.save_temp,args=(self.temp_sensor,"temp.csv",))
            self.in_process_save_temp = True
            self.process_save_temp.start()
            reply = 'oui'
        elif command == 'STOP_SAVE_TEMP':
            if self.in_process_save_temp:
                self.process_save_temp.terminate()
                self.in_process_save_temp = False
                reply = 'Process stopped'
            else:
                print("Can't stop save temp, not in process")
                logging.error("Can't stop save temp, not in process")
                reply = "Can't stop save temp, not in process"
                
                
        elif command == 'START_RECORDING':
            try:
                self.process_record = Process(target=self.camera.start_recording,args=("1920x1080",30,"/home/pi/Desktop/BaMMsat/record_continue",))
                self.in_process_record = True
                self.process_record.start()
                reply = 'Camera started recording'
                print("Camera started recording")
                logging.info("Camera started recording")
            except:
                print("Can't start the recording")
                logging.error("Can't start the recording")
        elif command == 'STOP_RECORDING':
            if self.in_process_record:
                self.in_process_record = False
                self.camera.kill_record()
                self.process_record.terminate()
                reply = 'Recording stopped'
            else:
                print("Can't stop recording, not in process")
                logging.error("Can't stop recording, not in process")
                reply = "Can't stop recording, not in process"

        elif command == 'SAVE_CURRENT':
            print('test')
            self.process_currrent = Process(target=self.save_current,args=("current.csv",))
            reply = 'Recording current'
        elif command == 'STOP_SAVE_CURRENT':
            self.process_currrent.terminate()
            reply = 'Stop Recording Current'
        
        elif command == 'AUTO_HEAT':
            self.process_auto_heat = threading.Thread(target = self.update_mosfets)
            self.in_process_auto_heat = True
            self.process_auto_heat.start()
            reply = 'Auto heat ON'
        elif command == 'STOP_AUTO_HEAT':
            if self.in_process_auto_heat:
                self.in_process_auto_heat = False
                for mosfet in self.mosfet_list:
                    mosfet.set_pwm(0)
                reply = 'Auto Heat stopped'
            else:
                print("Can't stop auto heat, not in process")
                logging.error("Can't stop auto heat, not in process")
                reply = "Can't stop auto heat, not in process"
        else:
            reply = 'No command found'
        return reply
    
    
    
    def establish_communication(self):
        if self.in_connection:
            print("Communication establish")
            logging.info("Communication establish")
            while True:
                data = self.connection.recv(1024)
                if not data == '':
                    data = data.decode('utf-8')
                    print('Data Received: {}'.format(data))
                    logging.info('Data Received: {}'.format(data))
                    data = data.split(' ',1)
                    command = data[0]
                    reply = self.__command_library(command,data)
                    if command == 'LOGOUT':
                        break
                    self.connection.sendall(reply.encode('utf-8'))
                    print('Reply sent')
                    logging.info('Reply sent')
        else:
            print("No Connection, Can't establish the communications")
            logging.error("No Connection, Can't establish the communications")
            
    def save_temp(self,sensor_list,filename):
        with open(filename,mode="a") as csv_file:
            csv_file.write("{0},{1},{2},{3},{4}\n".format("Date","Battery","Camera","Raspberry","CPU"))
            while True:
                temp = []
                for sensor in sensor_list:
                    temp.append(sensor.get_temp())
                csv_file.write("{0},{1},{2},{3},{4}\n".format(str(datetime.now()),str(temp[0]),str(temp[1]),str(temp[2]),str(self.get_temp_cpu())))
                logging.info("{0},{1},{2},{3},{4}\n".format(str(datetime.now()),str(temp[0]),str(temp[1]),str(temp[2]),str(self.get_temp_cpu())))
                csv_file.flush()
                sleep(self.interval_temp)
                
                
    def get_DutyCycle(self,temp):
        offset = 0
        temp = temp - offset
        upper_bound = 15
        lower_bound = 0
        diff = upper_bound - lower_bound
        pwm = -(temp/diff)*100 + 100
        print(pwm)
        if pwm > 100:
            pwm = 100
        if pwm < 0:
            pwm= 0
        if temp < 0:
            pwm = 100
        if pwm != 0:
            logging.info("PWM actif dutycyle: {}".format(pwm))
        return pwm
        
    def update_mosfets(self):
        while self.in_process_auto_heat:
            for k in range(len(self.mosfet_list)):
                temp = self.temp_sensor[k].get_temp()
                pwm = self.get_DutyCycle(temp)
                self.mosfet_list[k].set_pwm(pwm)
            sleep(self.interval_mosfet)
    
    def get_temp_cpu(self):
        cpu = CPUTemperature()
        return cpu.temperature
        
    
def __main__():
    log = Log("log_test.txt")
    server = Server('',5005)
    temp_raspberry= Temperature_Sensor(0x1A)
    temp_camera = Temperature_Sensor(0x19)
    temp_battery = Temperature_Sensor(0x18)
    server.set_temp_sensor([temp_battery,temp_camera,temp_raspberry])
    mosfet_camera = Mosfet(23)
    mosfet_battery = Mosfet(24)
    server.set_mosfets([mosfet_battery,mosfet_camera])
    cam = Camera("mjpeg")
    server.set_camera(cam)
    server.establish_connection()
    server.establish_communication()
    
__main__()