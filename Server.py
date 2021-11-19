###  BAAMSAT CAMERA PAYLOAD SERVER ###

import socket
import logging
import queue
import csv
import threading
import os
from datetime import datetime
from time import sleep
from multiprocessing import Process
from gpiozero import CPUTemperature
from temperature_Sensor import Temperature_Sensor
from mosfet import Mosfet
from camera import Camera
from current_sensor import Current_sensor
from auto_mode import AutoMode

"""
Class to instantiate the Logging system of the payload
"""
class Log:
    def __init__(self,filename):
        logging.basicConfig(filename=filename, format='[%(levelname)s] %(asctime)s: %(message)s',level=logging.INFO)
"""
Class to instantiate the server
"""    
class Server:
    def __init__(self,Host,Port): # Constructor of the class, specify the Host and the Port of the connection
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
    
    def set_automode(self,automode):
        self.auto_mode = automode
    
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket for the TCP connection
    connection = 0 
    process_save_temp = 0 # Process of Saving temp
    in_process_save_temp = False # Bool to keep track of in process or not
    in_connection = False 
    temp_sensor = [] # List of the temperature sensors in the payload
    interval_temp = 2 # Interval between the measurement of the temperature
    interval_mosfet = 2 # Interval between the update of the mosfets
    mosfet_list = [] # List of the mosfets in the payload
    process_auto_heat = 0  # Process of Auto Heat
    in_process_auto_heat = False
    camera = 0 # Save the camera object into the Server class
    process_record = 0 
    in_process_record = False
    process_currrent = 0
    process_time_lapse = 0
    in_process_time_lapse = False
    in_save_current = False
    auto_mode = 0
    in_auto_mode = False
    process_auto_mode = 0
    
    auto_heat_temp_treshold = 15 # Threshold for the activation of the Mosfet and so the heating system
    
    
    def __setup_connection(self): # Function to initiate the connection between the ground computer and the payload
        try:
            self.socket.listen(1) # Waiting for the connaciton
            print("Waiting for connection")
            logging.info("Waiting for connection")
            conn, addr = self.socket.accept()
            print("Connected with: {}".format(addr))
            logging.info("Connected with: {}".format(addr))
            return conn
        except:
            print("No connection found")
            logging.error("No connection found")
        
    def save_current(self,filename): # Function to save the current values inside a csv file
        with open(filename,mode="a") as csv_file:
                csv_file.write("{0},{1},{2},{3}\n".format("Date","Tension","Intensite","Puissance"))
                while True:
                    current = get_curent()
                    csv_file.write("{0},{1},{2},{3}\n".format(str(datetime.now()),str(current[0]),str(current[1]),str(current[2])))
                    csv_file.flush()
                    sleep(2)
    
    def establish_connection(self): # Function to establish the connection with the ground computer
        try:
            print("Connection on Port {} Open".format(self.Port))
            logging.info("Connection on Port {} Open".format(self.Port))
            self.socket.bind((self.Host,self.Port))
            self.connection = self.__setup_connection()
            self.in_connection = True
        except:
            print("Can't open connection")
            logging.error("Can't open connection")
    
    
    def __command_library(self,command,data): # Function containing the command dictionnary
        reply = ""
        if command == 'REPEAT': # REPEAT command to test the connection 
            reply = data[1]
        elif command == 'LOGOUT' or command == 'MODULE_OFF': # Logging out command
            print('System logout')
            reply = 'Server logging out'
            
        elif command == 'SAVE_TEMP': # Command to save launch the saving of the temperature 
            self.process_save_temp = Process(target=self.save_temp,args=(self.temp_sensor,"temp.csv",)) # create the process
            self.in_process_save_temp = True
            self.process_save_temp.start() # start the process
            reply = 'oui'
        elif command == 'STOP_SAVE_TEMP': # Command to stop the save of the temp
            if self.in_process_save_temp:
                self.process_save_temp.terminate()
                self.in_process_save_temp = False
                reply = 'Process stopped'
            else:
                print("Can't stop save temp, not in process")
                logging.error("Can't stop save temp, not in process")
                reply = "Can't stop save temp, not in process"
                
                
        elif command == 'VIDEO_RECORDING_START': # Command to start the recording
            try:
                self.process_record = Process(target=self.camera.start_recording,args=(self.camera.resolution_video,self.camera.fps,))
                self.in_process_record = True
                self.process_record.start()
                reply = 'Camera started recording'
                print("Camera started recording")
                logging.info("Camera started recording")
            except:
                print("Can't start the recording")
                logging.error("Can't start the recording")
                
        elif command == 'VIDEO_RECORDING_STOP': # Command to stop the recording
            if self.in_process_record:
                self.in_process_record = False
                self.camera.stop_recording()
                reply = 'Recording stopped'
            else:
                print("Can't stop recording, not in process")
                logging.error("Can't stop recording, not in process")
                reply = "Can't stop recording, not in process"
        
        elif command == "SET_VIDEO_RES": # Command to change the video resolution 
            self.camera.set_video_res(data[1])
            logging.info("Video resolution set to "+data[1])
            reply = "Video resolution set to "+data[1]
        
        elif command == "TIME_LAPSE_RECORDING_START": # Command to start the timelapse recording
            try:
                self.process_time_lapse = Process(target=self.camera.start_timelapse)
                self.in_process_time_lapse = True
                self.process_time_lapse.start()
                reply = 'Time Lapse started'
                print("Time Lapse started")
                logging.info("Time Lapse started")
            except:
                print("Can't start the Time Lapse")
                logging.error("Can't start the Time Laps")
            
        elif command == 'TIME_LAPSE_RECORDING_STOP': # COmmand to stop the Timelapse recording
            if self.in_process_time_lapse:
                self.in_process_time_lapse = False
                self.process_time_lapse.terminate()
                reply = 'Time Lapse stopped'
            else:
                print("Can't stop time lapse, not in process")
                logging.error("Can't stop time lapse, not in process")
                reply = "Can't stop time lapse, not in process"
                
        elif command == 'SET_TIME_LAPSE_RES': # Command to change the timelapse resolution
            self.camera.set_time_lapse_resolution(data[1])
            logging.info("Time Lapse resolution set to "+data[1])
            reply = "Time Lapse resolution set to "+data[1]
        
        elif command == "SET_TIME_LAPSE_IT": # Command to change the timelapse interval
            self.camera.set_timelaps_delay(int(data[1]))
            logging.info("Time Lapse interval set to "+data[1])
            reply = "Time Lapse interval set to "+data[1]
        
        elif command == "SET_VIDEO_FPS": # Command to change the fps of the recorded video
            self.camera.set_fps(int(data[1]))
            logging.info("Video FPS set to "+data[1])
            reply = "Video FPS set to "+data[1]

        elif command == 'SAVE_CURRENT': # Command to save the Current values
            self.in_save_current = True
            self.process_currrent = Process(target=self.save_current,args=("current.csv",))
            reply = 'Recording current'
        elif command == 'STOP_SAVE_CURRENT': # Command to stop the save of the current
            self.process_currrent.terminate()
            reply = 'Stop Recording Current'
        
        elif command == 'REBOOT': # Command to reboot the payload system, and so the raspberry pi
            os.system("sudo reboot")
            reply = 'Stop Recording Current'
                   
        elif command == 'GET_STATE': # Command to get the state of the payload
            reply = "\nCurrent state of the system:\nSAVE TEMP: {}\nSAVE CURRENT: {}\nAUTO HEAT: {}\nIN RECORD: {}\nIN TIMELAPSE: {}".format(self.in_process_save_temp,self.in_save_current,self.in_process_auto_heat,self.in_process_record,self.in_process_time_lapse)
        
        elif command == 'THERMAL_SET': # Command to change the temp threshold
            self.auto_heat_temp_treshold = int(data[1])
            print("Thermal auto heat set to "+data[1])
            logging.error("Thermal auto heat set to "+data[1])
            reply = "Thermal auto heat set to "+data[1]
        
        elif command == 'SENSOR_READ': # Command to get the temperature in live
            temp = self.read_temp(self.temp_sensor)
            reply="\nTemperature °C:\nBattery: {}\nCamera: {}\nRaspberry: {}".format(temp[0],temp[1],temp[2])
        
        elif command == 'DOWNLINK_IMAGE': # Command to get an image preview
            data = self.camera.get_image_downlink()
            print(data)
            reply=data
        
        elif command == 'AUTO_HEAT_START': # Command to start the autonomous heating system
            self.process_auto_heat = threading.Thread(target = self.update_mosfets)
            self.in_process_auto_heat = True
            self.process_auto_heat.start()
            reply = 'Auto heat ON'
        elif command == 'AUTO_HEAT_STOP': # Command to stop the heating system
            if self.in_process_auto_heat:
                self.in_process_auto_heat = False
                for mosfet in self.mosfet_list:
                    mosfet.set_pwm(0)
                reply = 'Auto Heat stopped'
            else:
                print("Can't stop auto heat, not in process")
                logging.error("Can't stop auto heat, not in process")
                reply = "Can't stop auto heat, not in process"

        elif command == 'AUTO_MODE_START':
            self.in_auto_mode = True
            self.process_auto_mode = Process(target=self.start_automode)
            self.process_auto_mode.start()
            reply = 'Auto Mode On'
        elif command == 'AUTO_MODE_STOP':
            self.in_auto_mode = False
            reply = 'Auto Mode Off'
        elif command == 'GET_AUTO_MODE_LIST':
            reply = self.auto_mode.print_command_list()
        elif command == 'ADD_COMMAND':
            com = data[1].split(' ',1)
            print(com)
            if len(com) == 2:
                self.auto_mode.add_command(com[0],com[1])
            else:
                self.auto_mode.add_command(com[0])
            reply = "command added"
        elif command == 'DELETE_COMMAND':
            self.auto_mode.delete_command(int(data[1]))
            reply = "command deleted"
        elif command == 'SAVE_COMMAND_HISTORY':
            self.auto_mode.save_command_history()
            reply='History saved'
        else:
            reply = 'No command found'
        return reply
    
    def start_automode(self):
        self.auto_mode.print_command_list()
        com,length = self.auto_mode.read_command()
        while com != None and self.in_auto_mode == True:
            self.__command_library(com,com)
            if length == None:
                pass
            else:
                sleep(int(length))
            self.auto_mode.print_command_list()
            com,length = self.auto_mode.read_command()


    def establish_communication(self): # Function that allow the communication between the ground and the payload
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
                    try:
                        self.connection.sendall(reply.encode('utf-8'))
                    except:
                        print(len(reply))
                        print(len(reply.ljust(1024)))
                        length = str(len(reply))
                        self.connection.sendall(length.encode('utf-8'))
                        self.connection.sendall(reply)
                    print('Reply sent')
                    logging.info('Reply sent')
        else:
            print("No Connection, Can't establish the communications")
            logging.error("No Connection, Can't establish the communications")
            
    def save_temp(self,sensor_list,filename): # Function to save the temp
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
    
    def read_temp(self,sensor_list): # function to answer the command Get temp
        temp = []
        for sensor in sensor_list:
            temp.append(sensor.get_temp())
        return temp
                
    def get_DutyCycle(self,temp): # Function to calculate the Duty Cycle of the PWM of a mosfet according to the temp
        offset = 0
        temp = temp - offset
        upper_bound = self.auto_heat_temp_treshold
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
        
    def update_mosfets(self): # Fonction to update the Duty Cycle of each masfets
        while self.in_process_auto_heat:
            for k in range(len(self.mosfet_list)):
                temp = self.temp_sensor[k].get_temp()
                pwm = self.get_DutyCycle(temp)
                self.mosfet_list[k].set_pwm(pwm)
            sleep(self.interval_mosfet)
    
    def get_temp_cpu(self): # Get the temp of the Raspberry Pi CPU
        cpu = CPUTemperature()
        return cpu.temperature

def get_nb_photos():
    nb_photo = 1
    fileName = "./images/timelaps_"+str(nb_photo)+".jpeg"
    while os.path.exists(fileName):
        nb_photo += 1
        fileName = "./images/timelaps_"+str(nb_photo)+".jpeg"
    return nb_photo     
    
def __main__(): # Main fonction of the Server
    nb_phot = get_nb_photos()
    log = Log("log_test.txt") # initiate the logging system
    server = Server('',5005) # Initiate the Server Object
    temp_raspberry= Temperature_Sensor(0x1A) # Declaration of the Temperature Sensors
    temp_camera = Temperature_Sensor(0x19)
    temp_battery = Temperature_Sensor(0x18)
    server.set_temp_sensor([temp_battery,temp_camera,temp_raspberry])
    mosfet_camera = Mosfet(23) # Declaration of the Mosfets
    mosfet_battery = Mosfet(24)
    server.set_mosfets([mosfet_battery,mosfet_camera])
    cam = Camera("mjpeg") # Declaration of the camera
    cam.set_nb_photos(nb_phot)
    auto_mode = AutoMode("command_AutoMode.pkl")
    server.set_automode(auto_mode)
    server.set_camera(cam)
    server.establish_connection() # Start the communication
    server.establish_communication()
    
    
__main__()