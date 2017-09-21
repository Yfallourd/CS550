import socket
import sys
import os
import threading
import timeit
from multiprocessing import Process


class Client:

    def __init__(self):
        print("Client initialized")

    def socketConnect(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip,port))
        except:
            print("Couldn't connect to "+str(ip))

        return sock

    def lookup(self, filename, sock):
        sock.send("lookup "+str(filename))
        data = sock.recv(4096)
        #todo

    def giveFile(self, filename, sock):
        f = open(filename, 'rb')
        fdata = f.read(4096)
        while(fdata):
            print("Sending file data")
            sock.send(fdata)
            fdata = f.read(4096)
        f.close()
        sock.shutdown(socket.SHUT_WR)
        print(sock.recv(4096))

    def getFile(self, filename, sock):
        f = open(filename, 'wb')
        sock.send("get "+str(filename))
        reply = sock.recv(4096)
        infos = reply.split("/")
        if infos[0]=="OK":
            sock.send("ACK")
            print("Receiving file data")
            fdata = sock.recv(4096)
            while(fdata):
                print("Receiving file data")
                f.write(fdata)
                fdata = sock.recv(4096)
        f.close()
        sock.shutdown(socket.SHUT_WR)
        print(sock.recv(4096))

class Server:

    def __init__(self):
        self.files = []
        self.host = "180.0.0.1"
        self.port = 12345
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def threadedListening(self):
        self.sock.listen(5)  #Limit to 5 concurrent connections
        while 1:
            client, ip = self.sock.accept()
            client.settimeout(120)  #Terminate after 2min of inactivity
            p = Process(target=self.Listen, args=(client, ip)).start()
            p.join()

    def Listen(self, client, ip):
        while 1:
            try:
                

            except:
                break



if __name__ == "__main__":
