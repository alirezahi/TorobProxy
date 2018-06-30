#! /usr/bin/python
# a simple udp client
import socket
import traceback

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dstHost = ('127.0.0.1', 5005)


def send_request(req):
    client.sendto(req, dstHost)
    resp = ""
    print('send success')
    while True:
        recv = client.recv(1024)
        if not recv:
            break
        resp += recv
    return resp


def http_request(http_content):
    msg = send_request(http_content.encode())
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
        content = 'GET / HTTP/1.1\r\nHost: ' + url + '\r\n'
        http_request(content)
    elif code == 404:
        print('status: not found')
        output_html = open("index.html", "w")
        output_html.write("<html>"
                          "<head><meta charset=\"utf-8\"></head>"
                          "<body>فایل مورد نظر یافت نشد :D</body>"
                          "</html>")
        output_html.close()
    else:
        output_html = open("index.html", "w")
        output_html.write("<html>"
                          "<head><meta charset=\"utf-8\"></head>"
                          "<body></body>"
                          "</html>")
        output_html.close()


try:
    header = '\r\n*\r\n'
    content = 'GET / HTTP/1.1\r\nHost: aut.ac.ir\r\n'
    http_request(content)
except:
    traceback.print_exc()
