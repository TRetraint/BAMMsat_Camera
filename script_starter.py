from subprocess import run
from time import sleep

file_path = "Server.py"

restart_timer = 2
def start_script():
    try:
        run("python "+filepath, check=False)
    except:
        handle_crash()

def handle_crash():
    print("crash")
    sleep(restart_timer)
    start_script()

start_script()