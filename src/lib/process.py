import socket
import sys
import subprocess
from multiprocessing import Process
import atexit

def exit_if_another_instance(unique_name):
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        lock_socket.bind('\0' + unique_name)
    except socket.error:
        sys.exit()

def run_in_background(args):
    process = Process(target=_run, args=[args])
    process.start()
    process.join()

def _run(args):
    subprocess.Popen(args, close_fds=True) # close_fds=True to prevent child process holding webserver port after it is killed.