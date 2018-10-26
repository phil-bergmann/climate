import sys
import os
import json
import socket
import SocketServer
import threading
import time
from time import localtime

configPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "light_config.json")

class Light(object):
    def __init__(self, configPath):
        self.configPath = configPath
        self.lightStatus = 0
        if self.loadConfig() == -1:
            sys.exit(-1)
        self.resetToConfig()
        
    def loadConfig(self):
        try:
            with open(self.configPath) as json_data_file:
                data = json.load(json_data_file)
            self.intensity = data['intensity']
            self.light_on = int(data['light_on'].split(":")[0])
            self.light_off = int(data['light_off'].split(":")[0])
        except:
            return -1
        
    def resetToConfig(self):
        pass
    
    def lightOn(self):
        pass
    
    def lightOff(self):
        pass
    
class ThreadedEchoRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # Echo the back to the client
        data = self.request.recv(1024)
        if data == '':
            return
        data = data.split(' ')
        if data[0] == 'lightOn':
            pass
        elif data[0] == 'lightOff':
            pass
        elif data[0] == 'reloadConfig':
            pass
        elif data[0] == 'setIntensity':
            pass
        return

class ThreadedEchoServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

address = ('localhost', 6000) # let the kernel give us a port
server = ThreadedEchoServer(address, ThreadedEchoRequestHandler)
#ip, port = server.server_address # find out what port we were given

t = threading.Thread(target=server.serve_forever)
t.setDaemon(True) # don't hang on exit
t.start()
#print 'Server loop running in thread:', t.getName()


while 1:
    #accept connections from outside
    (clientsocket, address) = serversocket.accept()
    #now do something with the clientsocket
    #in this case, we'll pretend this is a threaded server
    ct = client_thread(clientsocket)
    ct.run()