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
    print({
        'target':data['target'],
        'type':data['type'],
        'server': data['server']
    })
    if collection.find({
        'target':data['target'],
        'type':data['type'],
        'server': data['server']
    }).count() > 0:
        dns_response = collection.find_one({
            'target':data['target'],
            'type':data['type'],
            'server': data['server'],
        })
        data['response'] = dns_response['result']
        client_soc.send(bytes(json.dumps(data), encoding='utf_8'))
        client_soc.close()
        continue
    print('requested from server')
    result = []
    authoritative = False
    try:
        while not result:
            myResolver = dns.resolver.Resolver()
            myResolver.nameservers = [data['server']]
            myAnswers = myResolver.query(data['target'], data['type'])
            authoritative = bin(myAnswers.response.flags)[7]
            if data['type'] == 'A':
                result = [str(x) for x in myAnswers]
            if data['type'].upper() == 'CNAME':
                result = [str(x.target) for x in myAnswers]    
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
        'server': data['server'],
        'result': result,
        'authoritative':authoritative
    }
    response = {
        'target': data['target'],
        'type': data['type'],
        'server': data['server'],
        'result': result,
        'authoritative':authoritative
    }

    collection.insert_one(store)

    client_soc.send(bytes(json.dumps(response), encoding='utf_8'))

    client_soc.close()
