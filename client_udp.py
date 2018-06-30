#! /usr/bin/python
# a simple udp client
import socket
import time
import traceback

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dstHost = ('127.0.0.1', 5005)
while True:
        try:
            # header = 'asas\r\n*\r\n'
            content = 'GET / HTTP/1.1\r\nHost: aut.ac.ir\r\n'
            client.sendto((content.encode()), dstHost)
            print(time.time(), ' : send success')
            print(time.time()," : ",client.recv(1024))
            time.sleep(3)
        except:
            traceback.print_exc()
