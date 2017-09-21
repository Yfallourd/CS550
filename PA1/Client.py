import socket
import sys
import os
import threading
import timeit


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

    def addFile(self, filename, sock):
        f = open(filename, 'rb')

    def getFile(self, filename, sock):
        sock.send("get "+str(filename))
        reply = sock.recv(4096)
        infos = reply.split("/")



if __name__ == "__main__":
