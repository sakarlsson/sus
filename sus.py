#!/usr/bin/python
import SocketServer
import socket
import json
import subprocess
import os
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
    parser = OptionParser(__doc__)
    parser.add_option("-r", "--registry", dest="registry", default="gotburh05p:6379",
                      help="registry")
    (options, args) = parser.parse_args()

    print args[0]
    (host,port,protocol,version) = lookup(options.registry, args[0])

    env = {}
    for k  in  os.environ.keys():
        env[k] = os.environ[k]
        
    data = {'env':env, 'test':123.4}
    print "sending %s" % data
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print host
    print port 
    s.connect((host, port))
    s.send(json.dumps(data))
    result = json.loads(s.recv(1024))
    print result
    s.close()


if __name__ == '__main__':
    main()
