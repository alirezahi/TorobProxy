import ast
import datetime
from pymongo import MongoClient
import socket


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


def get_headers(data):
    header_line = data.splitlines()[0]
    header_line = ast.literal_eval(header_line)
    return header_line


def get_raw_data(data):
    return '\n'.join(str(data).splitlines()[2:])


UDP_IP = "127.0.0.1"
UDP_PORT = 5016

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.settimeout(1)

sock.bind((UDP_IP, UDP_PORT))


method_name = 'GET'
path = '/'
http_version = '1.1'

receive_data = True

deadline = None

whole_data = ''

while receive_data:
    await = True
    while await:
        await = False
        try:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            print(addr)
        except Exception as e:
            print('',end='')
            if deadline:
                print('',end='')
                break
            else:
                await = True
            pass
    if deadline:
        break
    now = datetime.datetime.now()
    data = data.decode('utf-8')

    if not deadline:
        whole_data += get_raw_data(data)

    # extract headers from received packet
    headers = get_headers(data)
    print(headers)

    print(headers['seq'])

    # get the seq number and send it back as ack
    ack = headers['seq']
    response_headers = str({'ack':ack})

    # check for the last packet
    if headers['end_flag']:
        deadline = datetime.datetime.now() + datetime.timedelta(seconds=1)
        print("**", whole_data, '**')

    sock.sendto(response_headers.encode(), addr)

# convert data to string to use it
whole_data = str(whole_data)

#find and extract the host address, method and http version to use it
host = find_host(whole_data)
http_describes = get_http_describes(whole_data)

# check if exists http request in cache
if False and collection.find({
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

        # end the connection if nothing is received
        if not recv:
            break
        
        http_data.append(recv)
        
        # send the received data to the client
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
