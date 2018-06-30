import socket
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client.proxy_db

collection = db.http_collection

def find_after(s, first):
    try:
        start = s.index(first) + len(first)
        return s[start:]
    except ValueError:
        return ""


def find_host(data):
    for line in data.splitlines():
        host = find_after(line, 'Host: ')
        host = host.strip()
        if host != '':
            return host


def get_http_describes(data):
    for line in data.splitlines():
        if line[:3] == 'GET':
            return line

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((UDP_IP, UDP_PORT))

while True:
    method_name = 'GET'
    path = '/'
    http_version = '1.1'

    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    data = data.decode('utf-8')

    # convert data to string to use it
    data = str(data)

    #find and extract the host address, method and http version to use it
    host = find_host(data)
    http_describes = get_http_describes(data)

    # check if exists http request in cache
    if collection.find_one({
        'host':host,
        'method':method_name,
        'path':path,
        'http_version': http_version
        }).count() > 0:
        http_response = collection.find_one({
            'host': host,
            'method': method_name,
            'path': path,
            'http_version': http_version
        })
        for data_packet in http_response['packets']:
            sent = sock.sendto(data_packet, addr)
    else:

        # open a TCP connection to send HTTP request
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # set server address and port
        server_address = (host, 80)

        # connect to server
        proxy_socket.connect(server_address)

        # sending ideal request to the connected server
        http_request = str(http_describes + '\r\nHost: ' + host + '\r\n\r\n')
        request_header = http_request.encode()
        proxy_socket.send(request_header)

        response = ''
        http_data = []

        while True:
            # send http request to main network
            recv = proxy_socket.recv(1024)

            # end the connection if nothing is recieved
            if not recv:
                break
            
            http_data.append(recv)
            
            # send the recieved data to the client
            sent = sock.sendto(recv, addr)

            # This is just for my debug :)))))))
            response += str(recv)
            print(str(recv))
            print('')

        # add data to cache to use it later
        collection.insert_one({
            'host': host,
            'method': method_name,
            'path': path,
            'http_version': http_version,
            'packets':http_data
        })

        proxy_socket.close()
