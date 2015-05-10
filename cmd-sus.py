#!/usr/bin/python
import SocketServer
import socket
import json
import subprocess

print socket.gethostname()

def register(name, host, port, protocol, version, timeout=10):
    value = "%s:%s:%s:%s" % (host, port, protocol,version)
    key = "service:%s" %name
    print "Registering %s" % key
    p = subprocess.Popen("./redis-cli set %s %s" % (key, value), shell=True, stdout=subprocess.PIPE)
    (stdout,stderr) = p.communicate()
    print stdout
    # print "Will expire in %d s" % timeout
    # p = subprocess.Popen("redis-cli expire %s %s" % (key, timeout), shell=True)
    # (stdout,stderr) = p.communicate()
    # print stdout


class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

class MyTCPServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = ""
        try:
            while True:
                packet = self.request.recv(1024)
                if len(packet):
                    data = data + packet
                else:
                    break
        except Exception, e:
            print "Exception while receiving message: ", e

        try:
            # process the data, i.e. print it:
            x = json.loads(data)
            print x
            # send some 'ok' back
            self.request.sendall(json.dumps({'return':'ok'}))
        except Exception, e:
            print "Exception wile receiving message: ", e

register("glugger", socket.gethostname(), 13373, "cmd", "1.0.0")

server = MyTCPServer((socket.gethostname(), 13373), MyTCPServerHandler)
server.serve_forever()


