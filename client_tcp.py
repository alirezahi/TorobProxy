import json
import socket
from ports import dns_port


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.settimeout(30)
soc.connect(('localhost', dns_port))

target = 'mail.google.com'
req_type = 'a'
server = '8.8.8.8'
query = {
    'target': target,
    'type': req_type,
    'server': server,
}
while True:
    soc.send(bytes(json.dumps(query), encoding='utf_8'))

    try:
        data = soc.recv(1024)
        data.rstrip('\0')
        print(data)
        break
    except Exception as e:
        print(e.args, 'receive time out!')

soc.close()
