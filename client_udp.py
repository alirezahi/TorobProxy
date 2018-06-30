#! /usr/bin/python
# a simple udp client
import socket
import traceback
import ast

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(1)
dstHost = ('127.0.0.1', 5005)


def send_request(req):
    header_length = 30
    packet_data_size = 1024 - header_length
    data = []
    for i in range(0, int(len(req)/packet_data_size) + 1):
        data.append(req[i * packet_data_size: (i+1) * packet_data_size])
    packet_index = 0
    while packet_index <= int(len(req)/packet_data_size):
        try:
            if packet_index == int(len(req)/packet_data_size):
                end_flag = 1
            else:
                end_flag = 0
            header = (str({'seq': packet_index % 2, 'end_flag': end_flag}) + '\r\n*\r\n').encode()
            client.sendto(header + data[packet_index], dstHost)
            recv = client.recv(1024)
            dict = ast.literal_eval(recv.decode())
            print('answer: ' + dict)
            if 'ack' in dict.keys() and dict['ack'] == packet_index % 2:
                packet_index += 1
        except:
            print("time out on receive ack " + str(packet_index % 2) + " packet")
    print('send success', req)
    resp = ""
    # while True:
    #     while True:
    #         try:
    #             recv = client.recv(1024)
    #             print('a: ' + recv.decode())
    #             resp += recv.decode()
    #             break
    #         except:
    #             print("time out on receive packets")
    return resp


def get_host_and_path(url):
    url_double_slash_place = url.find('//')
    if url_double_slash_place != -1:
        if url[:url_double_slash_place] == 'http:' or url[:url_double_slash_place] == 'https:':
            url = url[url_double_slash_place + len('//'):]
    url_slash_place = url.find('/')
    if url_slash_place == -1:
        host = url
        path = '/'
    else:
        host = url[:url_slash_place]
        path = url[url_slash_place:]
    return host, path


def http_request(http_content):
    msg = send_request(http_content.encode())
    return
    print("msg: ", msg)
    code = int(msg.split(" ")[1])
    if code == 200:
        print('status: ok')
        html_data = msg.split("<!doctype html>")[1]
        output_html = open("index.html", "w")
        output_html.write(html_data)
        output_html.close()
    elif code == 301 or code == 302:
        print('status: redirect')
        url = msg.split("Location: ")[1].split("\r")[0]
        host, path = get_host_and_path(url)
        new_http_content = 'GET ' + path + ' HTTP/1.1\r\nHost: ' + host + '\r\n'
        http_request(new_http_content)
    elif code == 404:
        print('status: not found')
        output_html = open("index.html", "w")
        output_html.write("<html>"
                          "<head><meta charset=\"utf-8\"></head>"
                          "<body>فایل مورد نظر یافت نشد :(</body>"
                          "</html>")
        output_html.close()
    else:
        print('status: undefined code')
        output_html = open("index.html", "w")
        output_html.write("<html>"
                          "<head><meta charset=\"utf-8\"></head>"
                          "<body>undefined http code :(</body>"
                          "</html>")
        output_html.close()


content = 'GET / HTTP/1.1\r\nHost: aut.ac.ir\r\n'
http_request(content)