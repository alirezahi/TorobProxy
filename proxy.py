import socket


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

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    data = data.decode('utf-8')
    
    # convert data to string to use it
    data = str(data)

    #find_between will find and extract the host address to use it
    host = find_host(data)

    # open a TCP connection to send HTTP request
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # set server address and port
    server_address = (host, 80)

    # connect to server
    proxy_socket.connect(server_address)

    # sending ideal request to the connected server
    request_header = str('GET / HTTP/1.0\r\nHost: '+host+'\r\n\r\n').encode()
    proxy_socket.send(request_header)

    response = ''
    while True:
        # send http request to main network
        recv = proxy_socket.recv(1024)

        # end the connection if nothing is recieved
        if not recv:
            break
        
        # send the recieved data to the client
        sent = sock.sendto(recv, addr)

        # This is just for my debug :)))))))
        response += str(recv)
        print(str(recv))
        print('')


    proxy_socket.close()
