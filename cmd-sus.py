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


def run(args, env, stdin):
    print args
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout,stderr) = p.communicate()
    rc = p.returncode
    return (stdout, stderr, rc)

class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True

class MyTCPServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = ""
        try:
            while True:
                print "recieveing"
                packet = self.request.recv(1024)
                if len(packet):
                    data = data + packet
                else:
                    break
        except Exception, e:
            print "Exception while receiving message: ", e

        try:
            # process the data, i.e. print it:
            cmdmessage = json.loads(data)
            cmdargs = cmdmessage['args']
            stdin = cmdmessage['stdin']
            print cmdargs
            print stdin
            (stdout, stderr, status) = run(["ls"] + cmdargs[1:], "", stdin)
            print "O %s %d" % (stdout, status)
            self.request.sendall(json.dumps({'status':status, 'stdout':stdout, 'stderr':stderr}))
        except Exception, e:
            print "Exception while receiving message: ", e



register("ls", socket.gethostname(), 13373, "cmd", "0.0.1")

server = MyTCPServer((socket.gethostname(), 13373), MyTCPServerHandler)
server.serve_forever()


