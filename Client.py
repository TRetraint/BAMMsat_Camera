###  BAAMSAT CAMERA PAYLOAD CLIENT ###

import socket
import logging
import cv2
import numpy as np
from time import sleep

"""
Class to instantiate the logging system of the client
"""
class Log:
    def __init__(self,filename):
        logging.basicConfig(filename=filename,format='[%(levelname)s] %(asctime)s:  %(message)s',level=logging.DEBUG)


"""
Client Class, allows the communication between the ground computer and the payload
"""
class Client:
    def __init__(self,TCP_IP,TCP_PORT,BUFFER_SIZE): # Class constructor
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT
        self.BUFFER_SIZE = BUFFER_SIZE
    
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # define the socket for the connection
    Connected = False

    def get_ip(self):
        return self.TCP_IP

    def get_port(self):
        return self.TCP_PORT
    
    def get_buffer_size(self):
        return self.BUFFER_SIZE
    
    def set_ip(self, TCP_IP):
        self.TCP_IP = TCP_IP
    
    def set_port(self, TCP_PORT):
        self.TCP_PORT = TCP_PORT

    def set_buffer_size(self, BUFFER_SIZE):
        self.BUFFER_SIZE = BUFFER_SIZE
    
    def establish_connection(self): # Allows to connect the client to the server, creating the bind
        print("Connecting to: {}".format(self.TCP_IP))
        logging.info("Connecting to: {}".format(self.TCP_IP))
        try:
            self.socket.connect((self.TCP_IP, self.TCP_PORT))
            print("Connection established")
            logging.info("Connection established")
            self.Connected = True
        except socket.error:
            print("Can't connect to the server: {}".format(self.TCP_IP))
            logging.error("Can't connect to the server: {}".format(self.TCP_IP))

    def close_connection(self): # End the connection 
        try:
            self.socket.close()
            print("Connection closed")
            logging.info("Connection closed")
        except :
            logging.error("Can't closed connection")

    def establish_communication(self): # Fonction allowing to send commands to the payload,and to receive live data
        if self.Connected == True:
            try:
                while True:
                    MESSAGE = input('Enter your message: ')
                    self.socket.send(str.encode(MESSAGE)) # Send the command
                    logging.info("Data send: {}".format(MESSAGE))
                    if MESSAGE == 'LOGOUT': # Closing the connection
                        self.close_connection()
                        break
                    elif MESSAGE == 'DOWNLINK_IMAGE': # exception for the downlink of an preview image
                        print("Image need to be taken and transfer, might take some time")
                        length = self.socket.recv(self.BUFFER_SIZE) # Get the size in bytes of the image to transfer
                        length = int(length)
                        print(length)
                        count = length//self.BUFFER_SIZE + 1 # Calculate the number of packs of bytes to download
                        data=b''
                        for i in range(count): # Loop until no more packs
                            newbuf = self.socket.recv(self.BUFFER_SIZE)
                            sleep(0.1)
                            if not newbuf: pass
                            data +=newbuf
                        data = np.frombuffer(data,dtype='uint8') # Convert the buffer into np array of int
                        decimg=cv2.imdecode(data,1) # Convert the array into an image
                        cv2.imshow('SERVER',decimg) # Plot the image
                        cv2.waitKey(0)
                        cv2.destroyAllWindows()
                    else:
                        data = self.socket.recv(self.BUFFER_SIZE) # Receiving the reply from the payload
                        data = data.decode('utf-8')
                        print("Received data: " + data)
                        logging.info("Received data: " + data)
            except:
                logging.error("Can't send the message")
        else:
            print("No connection detected")
            logging.error("No connection detected")

COM_PI = Client('169.254.92.26',5005,1024) # Create the client and connect it to the payload server
log = Log("log_test.txt")
COM_PI.establish_connection()
COM_PI.establish_communication()