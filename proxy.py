import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
    print("received message:", data)
    sent = sock.sendto(b'hello',addr)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('www.google.com', 80)
    client_socket.connect(server_address)

    request_header = b'GET / HTTP/1.0\r\nHost: www.google.com\r\n\r\n'
    client_socket.send(request_header)

    response = ''
    while True:
        recv = client_socket.recv(1024)
        if not recv:
            break
        response += str(recv)
        print(str(recv))
        print('')

    # print(response)
    client_socket.close()
