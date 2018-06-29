#! /usr/bin/python
# a simple udp client
import socket
import time
import traceback

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dstHost = ('127.0.0.1', 5005)
while True:
        try:
            client.sendto(b'GET / HTTP/1.1\r\nHost: aut.ac.ir', dstHost)
            print(time.time(), ' : send success')
            print(time.time()," : ",client.recv(1024))
            time.sleep(3)
        except:
            traceback.print_exc()