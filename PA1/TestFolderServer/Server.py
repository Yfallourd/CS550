import socket
import timeit
import threading
from collections import defaultdict

class Server:

    def __init__(self):
        self.files = defaultdict(list)  #Data structure : dictionnary of lists
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 12341
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def register(self, filename, hostip):
        if hostip in self.files[filename]:
            return ""
        else:
            self.files[filename].append(hostip)
            return "File successfully added"

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
        print("Server socket listening on port "+str(self.port)+"...")
        while 1:
            client, ip = self.sock.accept()
            print("Connection received from " + str(client.getsockname()[0]))
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
                print("Current file list :\n")
                print(str(self.files))
            elif infos[0] == "register":
                result = self.register(infos[1], infos[2])
                client.send(result.encode())
                client.shutdown(socket.SHUT_WR)
                print("Current file list :\n")
                print(str(self.files))
            else:
                client.send("Unrecognized command".encode())


if __name__ == "__main__":
    server = Server()
    print(server.host)
    server.threadedListening()
