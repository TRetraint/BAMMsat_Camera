import subprocess
import os, signal
from time import sleep

class Camera():
    def __init__(self,input_format):
        self.input_format = input_format
        
    process = 0
    nb_video = 1
    stop_record = False
        
    def start_recording(self,resolution,framerate,output_file):
        sleep(1500)
        while self.stop_record == False:
            self.process = subprocess.Popen(["ffmpeg","-f","v4l2","-input_format",self.input_format,"-framerate",str(framerate),"-video_size",str(resolution),"-i","/dev/video0","-c:v","copy",output_file+str(self.nb_video)+".mkv"])
            sleep(60)
            self.nb_video = self.nb_video + 1
            self.stop_recording()
            sleep(5)
        
    def stop_recording(self):
        for line in os.popen("ps ax | grep " + "ffmpeg" + " | grep -v grep"):
            fields = line.split()
            pid = fields[0]
            os.kill(int(pid),signal.SIGKILL)
    
    def kill_record(self):
        self.stop_record = True