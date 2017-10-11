import socket
import threading
from multiprocessing import Process, Pool
from collections import defaultdict

class Server:

    def __init__(self):
        self.files = defaultdict(list)  #Data structure : dictionnary of lists
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 12001
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def fireSignals(self):
        pool = Pool(4)
        ports = [12301]
        #ports = [12346, 12347, 12348, 12349] #Change this according to how many concurrent clients you want
        pool.map(self.signal, ports)
        pool.close()
        pool.join()

    def signal(self, port):
        #send test start signal to awaiting client
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if sock:
            sock.connect(("127.0.1.1", port))
            sock.shutdown(socket.SHUT_WR)

    def register(self, filename, hostip):
        if hostip in self.files[filename]:
            return ""   #File was already added so nothing happens
        else:
            self.files[filename].append(hostip)
            return filename + " successfully added"

    def search(self, filename):
        if filename in self.files:
            portstring = ""
            for each in self.files[filename]:
                portstring += str(each) + " "
            if len(self.files[filename]) == 1:
                return "Client on port " + portstring.strip() + " has this file"
            else:

                return "Clients on ports " + portstring.strip() + " have this file"
        else:
            return "404 - No peer has registered this file"

    def threadedListening(self):
        self.sock.listen()  # Limit to 5 concurrent connections
        print("Server socket listening on port "+str(self.port)+"...\n")
        while 1:
            client, ip = self.sock.accept() #Program waits here for a call from a client
            print("\nConnection received from " + str(client.getsockname()[0]))
            client.settimeout(120)  # Terminate after 2min of inactivity
            threading._start_new_thread(self.Listen, (client, ip))


    def Listen(self, client, ip):
        data = client.recv(4096).decode()
        if data:
            infos = data.split(" ")
            if infos[0] == "lookup":
                result = self.search(infos[1])
                client.send(result.encode())
                client.shutdown(socket.SHUT_WR)
                print("\nCurrent file list :")
                print(str(self.files))
            elif infos[0] == "register":
                result = self.register(infos[1], infos[2])
                client.send(result.encode())
                client.shutdown(socket.SHUT_WR)
                print("\nCurrent file list :")
                print(str(self.files))
            else:
                client.send("Unrecognized command".encode())


if __name__ == "__main__":
    server = Server()
    print("Local IP is : " + server.host)
    while 1:
        result = input("\nInput START to boot the server or "
                       "TEST to fire test signals to the clients\n")
        if result == "START":
            server.threadedListening()
        elif result == "TEST":
            server.fireSignals()
            server.threadedListening()
