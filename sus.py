#!/usr/bin/python
import SocketServer
import socket
import json
import subprocess
import os
import sys
from optparse import OptionParser

def lookup(registry, name):
    (host,port) = registry.split(":")
    key = "service:%s" % name
    print "./redis-cli --csv -h %s -p %s get %s" % (host, port, key)
    p = subprocess.Popen("./redis-cli --csv -h %s -p %s get %s" % (host, port, key), shell=True, stdout=subprocess.PIPE)
    (stdout,stderr) = p.communicate()
    services = stdout.split(",")
    for service in services:
        (host,port,protocol,version) = service.lstrip('"').rstrip('"').split(":")
        print "h %s, p %s, proto %s, v %s" % (host,port,protocol,version)
        return (host,int(port),protocol,version)
        


def main():
    registry = os.environ['SUSREG']
    (host,port,protocol,version) = lookup(registry, sys.argv[1])

    print "X"
    
    env = {}
    for k  in  os.environ.keys():
        env[k] = os.environ[k]

    stdin = sys.stdin.read()
    data = {'env':env, 'args':sys.argv[1:], 'stdin':stdin }
    print "sending %s" % data

    print "X"
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print host
    print port 
    s.connect((host, port))
    msg = json.dumps(data)
    msglen = len(data)
    totalsent = 0
    print "X"
    while totalsent < msglen:
        print "sending"
        sent = s.send(msg[totalsent:])
        totalsent = totalsent + sent
    s.shutdown(1)
    print "recieveing"
    packets = ""
    while True:
        print "recieveing"
        packet = s.recv(1024)
        print "got %d" % len(packet)
        if len(packet):
            packets = packets + packet
        else:
            break
    response = json.loads(packets)
    print response['stdout']
    s.close()
    exit response['status']

if __name__ == '__main__':
    main()
