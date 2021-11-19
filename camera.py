###  BAAMSAT CAMERA PAYLOAD CAMERA CLASS ###

import subprocess
import os, signal
from time import sleep
import cv2
import numpy as np

"""
Class to instanciate the camera features of the payload
"""
class Camera():
    def __init__(self,input_format):
        self.input_format = input_format
        self.process = 0
        self.nb_video = 1
        self.stop_record = False
        self.stop_timelapse = False
        self.timelapse_delay = 2
        self.nb_photos = 1
        self.resolution_video = "1920x1080"
        self.fps = 30
        self.resolution_time_lapse = "3840x2160"
    
    """
    Function to start the recording, using the mjpg_streamer library
    """
    def start_recording(self,resolution,framerate):
        command = 'mjpg_streamer -i "/usr/local/lib/mjpg-streamer/input_uvc.so -r '+resolution+'" -o "/usr/local/lib/mjpg-streamer/output_file.so -f /home/pi/Desktop/BaMMsat/videos -d 50"'
        self.process = subprocess.Popen(command,shell=True)
        
    def stop_recording(self): # Function to stop the recording
        for line in os.popen("ps ax | grep " + "mjpg_streamer" + " | grep -v grep"): # Find the process named mjpg_streamer in the tasks
            fields = line.split() 
            pid = fields[0] # Get the PID of the process
            os.kill(int(pid),signal.SIGKILL) # Kill the process using the PID
            
    def start_timelapse(self): # Function to start the timelapse
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,3840) # Set the width resolution
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160) # Set the height resolution
        while(self.stop_timelapse == False): # Take picture till the user ask to stop it
            ret,frame = cap.read() # Read the frame from the camera
            cv2.imwrite("images/timelaps_" + str(self.nb_photos)+".jpeg",frame) # Save the picture as a jpg file
            self.nb_photos += 1
            sleep(self.timelapse_delay) # Delay between 2 pictures
            
    def stop_timelapse(self): # Function to stop the timelapse
        self.stop_timelapse = True
            
    def set_timelaps_delay(self,delay): #Function to change the delay of the timelapse
        self.timelapse_delay = delay
        
    def kill_record(self):
        self.stop_record = True
    
    def set_video_res(self,resolution): # Change the resolution of the video
        self.resolution_video = resolution
    
    def set_fps(self,fps): # Change the fps of the record 
        self.fps = fps
    
    def set_time_lapse_resolution(self,resolution): # Change the timelapse resoltion
        self.resolution_time_lapse = resolution
        
    def get_image_downlink(self): # Function to take a picture and to encode it to bytes to upload to the ground computer
        cap = cv2.VideoCapture(0) 
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)        
        for i in range(5): # Take 5 differents pictures to avoid camera issues
            ret,frame = cap.read()
            sleep(2)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90] # Encoding parameter for the image
        result, imgencode = cv2.imencode('.jpg',frame,encode_param) # Encode the image
        data = np.array(imgencode) 
        stringData = data.tostring() #Convert the image to a string of bytes
        return stringData
        
    def set_nb_photos(self,nb):
        self.nb_photos = nb
