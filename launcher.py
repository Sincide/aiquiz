#!/usr/bin/env python3
import os
import sys
import time
import subprocess
import socket

def is_port_open(port):
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    # Change to app directory
    os.chdir('/home/martin/aiquiz')
    
    # Check if server already running
    if is_port_open(5000):
        # Just open browser
        subprocess.Popen(['/usr/bin/brave', 'http://localhost:5000'], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return
    
    # Start Flask server
    subprocess.Popen(['/usr/bin/python', 'app.py'], 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for server to start
    time.sleep(3)
    
    # Open browser
    subprocess.Popen(['/usr/bin/brave', 'http://localhost:5000'], 
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main() 