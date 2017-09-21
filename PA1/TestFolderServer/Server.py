import sys
import socket
import os
import timeit
import time
from multiprocessing import Process, Lock, SimpleQueue



class Server:

    def __init__(self):
        self.files = {}
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 12341
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def register(self, filename, hostip, out_q):
        outdict = {}
        if filename in self.files:
            return "A file with this name already exists"
        else:
            outdict[filename] = hostip
            out_q.put(outdict)
            print("Si c'est ça j'te nique" +str(out_q.get()))
            return "File successfully added"

    def search(self, filename, out_q):
        print(str(self.files))
        if filename in self.files:
            return str(self.files[filename])
        else:
            return "404"

    def threadedListening(self):
        self.sock.listen()  # Limit to 5 concurrent connections
        print("Server socket listening on port "+str(self.port)+"...")
        out_q = SimpleQueue()
        while 1:
            client, ip = self.sock.accept()
            print("Connection received from " + str(client.getsockname()[0]))
            client.settimeout(120)  # Terminate after 2min of inactivity
            p = Process(target=self.Listen, args=(client, ip, out_q))
            p.start()
            print(str(out_q.get()))
            self.files.update(out_q.get())
            p.join()
            print("youpi")


    def Listen(self, client, ip, out_q):
        print("Listen : "+str(self.files))
        print(str(os.getpid())+" is currently in the Listen method")
        data = client.recv(4096).decode()
        if data:
            infos = data.split(" ")
            if infos[0] == "lookup":
                client.send(self.search(infos[1], out_q).encode())
                print(str(self.files))
            elif infos[0] == "register":
                result = self.register(infos[1], infos[2], out_q)
                client.send(result.encode())
                print(str(self.files))
            else:
                client.send("Unrecognized command".encode())
                out_q.put({})


if __name__ == "__main__":
    server = Server()
    print(server.host)
    server.threadedListening()
