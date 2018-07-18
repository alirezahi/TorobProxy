import json
import socket
import dns.resolver
from ports import dns_port
from pymongo import MongoClient
import time


client = MongoClient('localhost', 27017)

db = client.proxy_dns_db

collection = db.dns_collection


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(('localhost', dns_port))
soc.listen(1)
while True:
    client_soc, addr = soc.accept()
    data = client_soc.recv(1024)
    data = json.loads(str(data, encoding='utf_8'))
    print(data)
    if collection.find({
        'target':data['target'],
        'type':data['type'],
    }).count() > 0:
        dns_response = collection.find_one({
            'target':data['target'],
            'type':data['type'],
        })
        if int(time.time()) - dns_response['time'] <= dns_response['ttl']:
            data['response'] = dns_response['result']
            client_soc.send(bytes(json.dumps(data), encoding='utf_8'))
            client_soc.close()
            continue
        else:
            print('ttl is over!')
            db.remove((request.target == data['target']) & (request.type == data['type']))
    print('requested from server')
    result = []
    try:
        while not result:
            myResolver = dns.resolver.Resolver()
            myResolver.nameservers = [data['server']]
            myAnswers = myResolver.query(data['target'], data['type'])
            result = [str(x) for x in myAnswers]
    except dns.exception.Timeout:
        print('time out')
    except dns.resolver.NoAnswer as e:
        client_soc.send(bytes(json.dumps({'error':e.args[0]}), encoding='utf_8'))
        break
    except Exception as e:
        print(e.args)
        continue
    store = {
        'target': data['target'],
        'type': data['type'],
        'ttl': ttl,
        'time': int(time.time()),
        'result': result
    }
    response = {
        'result':result
    }
    print(result)

    client_soc.send(bytes(json.dumps(response), encoding='utf_8'))

    data['response'] = result
    # client_soc.send(bytes(json.dumps(data), encoding='utf_8'))
    client_soc.close()
