import socket
import timeit
import sys
from multiprocessing import Process


class Client:
    def __init__(self):
        print("Client initialized")

    def socketConnect(self, ip, port):
        try:
            so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            so.connect((ip, port))
            print("Connected to " + str(ip) + " on port " + str(port))
            return so
        except:
            print("Couldn't connect to " + str(ip))


    def register(self, filename, sock):
        sock.send("register "+ filename)

    def lookup(self, filename, sock):
        sock.send("lookup " + filename)
        data = sock.recv(4096)
        # todo

    def getFile(self, filename, sock):
        f = open(filename, 'wb')
        sock.send("get " + str(filename))
        print("Receiving file data")
        fdata = sock.recv(4096)
        while (fdata):
            print("Receiving file data")
            f.write(fdata)
            fdata = sock.recv(4096)
        f.close()
        sock.shutdown(socket.SHUT_WR)
        print(sock.recv(4096))


class Server:
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 12345
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def giveFile(self, filename, sock):
        f = open(filename, 'rb')
        fdata = f.read(4096)
        while (fdata):
            print("Sending file data")
            sock.send(fdata)
            fdata = f.read(4096)
        f.close()
        sock.shutdown(socket.SHUT_WR)
        print(sock.recv(4096))

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


if __name__ == "__main__":

    server = Server()
    client = Client()

    while True:
        userinput = input(
            "Enter commmand:\n"
            " \"get\" to download a file.\n"
            " \"register\" to index one of your files\n"
            " \"lookup\" to query for a desired file location\n"
            " \"exit\" to quit the program\n")
        if userinput == "get":
            userinput = input("Filename ?\n")
            ip = input("File host IP ?\n")
            port = input("File host port ?\n")
            sock = client.socketConnect(ip, port)
            client.getFile(userinput, sock)
            print("Issued GET request.\n")
        elif userinput == 'register':
            filename = input("Filename ?\n")
            ip = input("Indexing server IP ?\n")
            port = input("Indexing server port ?\n")
            sock = client.socketConnect(ip, port)
            client.register(filename, sock)
            print("Issued PUT request.\n")
        elif userinput == 'lookup':
            filename = input("Filename ?\n")
            ip = input("Indexing server IP ?\n")
            port = input("Indexing server port ?\n")
            sock = client.socketConnect(ip, port)
            client.lookup(filename, sock)
        elif userinput == 'exit':
            sys.exit()
        else:
            print("Incorrect command.\n")
