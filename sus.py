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
    p = subprocess.Popen("./redis-cli --csv -h %s -p %s get %s" % (host, port, key), shell=True, stdout=subprocess.PIPE)
    (stdout,stderr) = p.communicate()
    services = stdout.split(",")
    for service in services:
        (host,port,protocol,version) = service.lstrip('"').rstrip('"').split(":")
        return (host,int(port),protocol,version)
        


def main():
    args = sys.argv
    if( args[1] == "-i"):
        args = args[1:]
        use_stdin=True
    else:
        use_stdin=False
    registry = os.environ['SUSREG']
    (host,port,protocol,version) = lookup(registry, args[1])

    env = {}
    for k  in  os.environ.keys():
        env[k] = os.environ[k]

    if (use_stdin):
        stdin = sys.stdin.read()
    else:
        stdin = ""
        
    data = {'env':env, 'args':args[1:], 'stdin':stdin }
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    msg = json.dumps(data)
    msglen = len(data)
    totalsent = 0
    while totalsent < msglen:
        sent = s.send(msg[totalsent:])
        totalsent = totalsent + sent
    s.shutdown(1)
    packets = ""
    while True:
        packet = s.recv(1024)
        if len(packet):
            packets = packets + packet
        else:
            break
    response = json.loads(packets)
    sys.stdout.write(response['stdout'])
    s.close()
    sys.exit(response['status'])

if __name__ == '__main__':
    main()
