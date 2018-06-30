#! /usr/bin/python
# a simple udp client
import socket
import time
import traceback

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dstHost = ('127.0.0.1', 5005)
# while True:
try:
    client.sendto(b'GET / HTTP/1.1\r\nHost: aut.ac.ir', dstHost)
    msg = ""
    print(time.time(), ' : send success')
    while True:
        recv = client.recv(1024)
        if not recv:
            break
        msg += recv

except:
    traceback.print_exc()