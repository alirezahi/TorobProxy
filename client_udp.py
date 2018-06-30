#! /usr/bin/python
# a simple udp client
import socket
import traceback

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dstHost = ('127.0.0.1', 5005)


def send_request(req):
    try:
        client.sendto(req, dstHost)
        resp = ""
        print('send success')
        while True:
            recv = client.recv(1024)
            if not recv:
                break
            resp += recv.decode()
    except:
        traceback.print_exc()
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
                          "<body>File not found! :D</body>"
                          "</html>")
        output_html.close()
    else:
        print('status: undefined code')
        output_html = open("index.html", "w")
        output_html.write("<html>"
                          "<head><meta charset=\"utf-8\"></head>"
                          "<body></body>"
                          "</html>")
        output_html.close()


header = '\r\n*\r\n'
content = 'GET / HTTP/1.1\r\nHost: aut.ac.ir\r\n'
http_request(content)

