import ast
import datetime
from pymongo import MongoClient
import socket
from ports import main_port
import requests

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


def send_request(req, addr):
    header_length = 30
    packet_data_size = 1024 - header_length
    data = []
    for i in range(0, int(len(req)/packet_data_size) + 1):
        data.append(req[i * packet_data_size: (i+1) * packet_data_size])
    packet_index = 0
    while packet_index <= int(len(req)/packet_data_size):
        # print(packet_index,' packet_index')
        # print(int(len(req)/packet_data_size), ' int(len(req)/packet_data_size)')
        try:
            if packet_index == int(len(req)/packet_data_size):
                end_flag = 1
            else:
                end_flag = 0
            header = (str({'seq': packet_index % 2, 'end_flag': end_flag}) + '\r\n*\r\n').encode('utf-8')
            sock.sendto(header + data[packet_index], addr)
            recv = sock.recv(1024)
            dict = ast.literal_eval(recv.decode('utf-8'))
            # print('answer: ' , dict)
            if 'ack' in dict.keys() and dict['ack'] == packet_index % 2:
                packet_index += 1
        except Exception as e:
            print("error on {}: {}".format(packet_index%2, e))
    print('send success')


UDP_IP = "127.0.0.1"
UDP_PORT = main_port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.settimeout(1)

sock.bind((UDP_IP, UDP_PORT))


method_name = 'GET'
path = '/'
http_version = '1.1'

receive_data = True

deadline = None

last_ack = ''

whole_data = ''

while receive_data:
    await = True
    while await:
        await = False
        try:
            data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
            # print(addr)
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
    try:
        data = data.decode('utf-8')

        # extract headers from received packet
        headers = get_headers(data)

        # get the seq number and send it back as ack
        ack = headers['seq']
        response_headers = str({'ack':ack})

        if not deadline and ack != last_ack:
            whole_data += get_raw_data(data)

        last_ack = ack

        # check for the last packet
        if headers['end_flag']:
            deadline = datetime.datetime.now() + datetime.timedelta(seconds=1)

        sock.sendto(response_headers.encode('utf-8'), addr)
    except:
        pass


# convert data to string to use it
whole_data = str(whole_data)



#find and extract the host address, method and http version to use it
host = find_host(whole_data)
http_describes = get_http_describes(whole_data)

print('here')
# check if exists http request in cache
initial_path = path
if collection.find({
    'host':host,
    'method':method_name,
    'path':path,
    'http_version': http_version
    }).count() > 0:
    print('found in cache')
    http_response = collection.find_one({
        'host': host,
        'method': method_name,
        'path': path,
        'http_version': http_version
    })
    send_request(http_response['data'].encode('utf-8'), addr)
else:


    # open a TCP connection to send HTTP request
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    proxy_socket.settimeout(1)

    # set server address and port
    server_address = (host, 80)

    # connect to server
    try:
        proxy_socket.connect(server_address)
    except:
        print('undefined host')
        proxy_socket.close()
        send_request("<html>"
                          "<head><meta charset=\"utf-8\"></head>"
                          "<body>هاست مورد نظر یافت نشد :(</body>"
                          "</html>".encode('utf-8'), addr)
        exit()
    # sending ideal request to the connected server
    http_request = str(http_describes + '\r\nHost: ' + host + '\r\n\r\n')
    path = http_request.split(' ')[1]
    # request_header = http_request.encode('utf-8')
    # proxy_socket.send(request_header)
    r = requests.get('http://'+host+path)
    if r.status_code == 404:
        response = "<html>"+"<head><meta charset=\"utf-8\"></head>"+"<body>فایل مورد نظر یافت نشد :(</body>"+"</html>";
    else:
        response = r.text

    # await = True
    # while await:
    #     # send http request to main network
    #     await = False
    #     try:
    #         recv = proxy_socket.recv(1024)
    #     except:
    #         # end the connection if nothing is received
    #         break
    #
    #     # end the connection if nothing is received
    #     if not recv:
    #         break
    #
    #
    #     # send the received data to the client
    #     sent = sock.sendto(recv, addr)
    #
    #     response += str(recv)
    # print(str(response))
    print('data received from server')

    # add data to cache to use it later
    collection.insert_one({
        'host': host,
        'method': method_name,
        'path': initial_path,
        'http_version': http_version,
        'data':response,
    })

    proxy_socket.close()
    send_request(response.encode('utf-8'), addr)
