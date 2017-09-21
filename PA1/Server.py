import sys
import socket
import timeit
from multiprocessing import Process

class Server:

    def __init__(self):
        self.files = {}
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 12346
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def register(self, filename, hostip):
        

    def threadedListening(self):
        self.sock.listen(5)  # Limit to 5 concurrent connections
        print("Server socket listening..._")
        while 1:
            client, ip = self.sock.accept()
            client.settimeout(120)  # Terminate after 2min of inactivity
            p = Process(target=self.Listen, args=(client, ip)).start()
            p.join()

    def Listen(self, client, ip):
        try:
            data = client.recv(4096)
            infos = data.split()
            if infos[0] == "get":
                self.giveFile(infos[1], client)
        except:
            print("woops lol")