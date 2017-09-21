import socket
import timeit
import sys
from multiprocessing import Process, Lock, Queue
from os import walk


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
        sock.send(("register " + filename + " ").encode())

    def findAllFiles(self):
        files = []
        for (dirpath, dirnames, filenames) in walk("."): #parse all directories and files
            files.extend(filenames)
            break   #break after one iteration to remain at the same level
        if "Client.py" in files:
            files.remove("Client.py")
        if "Server.py" in files:
            files.remove("Server.py")
        return files

    def lookup(self, filename, sock):
        sock.send(("lookup " + filename).encode())
        print(sock.recv(4096).decode())

    def getFile(self, filename, sock):
        f = open(filename, 'wb')
        sock.send(("get " + str(filename)).encode())
        print("Receiving file data")
        fdata = sock.recv(4096).decode()
        while (fdata):
            print("Receiving file data")
            f.write(fdata)
            fdata = sock.recv(4096).decode()
        f.close()
        sock.shutdown(socket.SHUT_WR)
        print(sock.recv(4096).decode())


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
        print(sock.recv(4096).decode())

    def threadedListening(self):
        self.sock.listen(5)  # Limit to 5 concurrent connections
        lock = Lock()
        lock.acquire()
        print("\n[LISTENING PROCESS]\nServer socket listening...")
        lock.release()
        while 1:
            client, ip = self.sock.accept()
            print("Connection received from "+str(client.getsockname()[0])+" "+str(client.getsockname()[1]))
            client.settimeout(120)  # Terminate after 2min of inactivity
            p = Process(target=self.Listen, args=(client, ip, lock)).start()
            p.join()

    def Listen(self, client, ip, lock):
        data = client.recv(4096).decode()
        infos = data.split(" ")
        if infos[0] == "get":
            lock.acquire()
            self.giveFile(infos[1], client)
            lock.release()


if __name__ == "__main__":

    server = Server()
    client = Client()
    listenerProcess = Process(target=server.threadedListening).start()
    while True:
        userinput = input(
            "Enter commmand:\n"
            " \"get\" to download a file.\n"
            " \"register\" to index one of your files\n"
            " \"lookup\" to query for a desired file location\n"
            " \"exit\" to quit the program\n"
            "or let the program run for the server to listen\n")
        if userinput == "get":
            userinput = input("Filename ?\n")
            ip = input("File host IP ?\n")
            port = input("File host port ?\n")
            sock = client.socketConnect(ip, int(port))
            client.getFile(userinput, sock)
            print(sock.recv(4096).decode())
            sock.shutdown(socket.SHUT_WR)
        elif userinput == 'register':
            files = client.findAllFiles()
            ip = input("Indexing server IP ?\n")
            port = input("Indexing server port ?\n")
            sock = client.socketConnect(ip, int(port))
            for f in files:
                client.register(f, sock)
                print(sock.recv(4096).decode())
                sock = client.socketConnect(ip, int(port))
            sock.shutdown(socket.SHUT_WR)
        elif userinput == 'lookup':
            filename = input("Filename ?\n")
            ip = input("Indexing server IP ?\n")
            port = input("Indexing server port ?\n")
            sock = client.socketConnect(ip, int(port))
            client.lookup(filename, sock)
            print(sock.recv(4096).decode())
            sock.shutdown(socket.SHUT_WR)
        elif userinput == "exit":
            print("warning, this will also terminate the server process\n")
            input = input("Are you sure ? (y/n)\n")
            if input == "y":
                listenerProcess.join()
                sys.exit()
        else:
            print("Incorrect command.\n")