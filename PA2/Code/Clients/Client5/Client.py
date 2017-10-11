import socket
import threading
import datetime
import sys
import time
from multiprocessing import Process
from os import walk, path, listdir, remove
import random


class Client:
    def __init__(self):
        print("Client initialized")

    def testAverageReqTime(self, servers, N, test, port):
        start = datetime.datetime.now()
        end = start
        if test == "lookup":
            for i in range(N):  # lookup different filenames, some being found and others not
                filename = "c"+str(i % 8)+"-1"
                self.decentralizedLookup(filename, servers)
            end = datetime.datetime.now()
        elif test == "register":
            for i in range(N):  # register all the files multiple time
                self.registerAllFiles(servers, port)
            end = datetime.datetime.now()
        elif test == "get":
            for i in range(N):  # get a random file from a random peer, repeated N times
                target = random.choice([12341,12342,12343,12344,12345,12346,12347,12348])
                filename = "c"+list(str(target))[4]+"-"+random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
                sock = client.socketConnect("127.0.1.1", target)
                if sock:
                    self.getFile(filename, sock)
                    sock.shutdown(socket.SHUT_WR)

            end = datetime.datetime.now()
        delta = end - start
        return [(delta.total_seconds())/N, (N/delta.total_seconds())]

    def testMulti(self, servers, N, test, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("127.0.1.1", 12305))  # Defines peer's port for test
        sock.listen()
        print("\nClient ready and awaiting start signal from server\n")
        client, clientip = sock.accept()
        time.sleep(0.5)
        print("Signal received, starting test\n")
        result = self.testAverageReqTime(servers, N, test, port)
        print("\n[The average request took " + str(result[0]) + " seconds]\n")
        print("\n[The throughput is  " + str(result[1]) + " operations per second]\n")

    def selectServer(self, servers):
        #This is where we'd normally select based on performance
        return random.choice(servers)

    def socketConnect(self, ip, port):
        try:
            so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            so.connect((ip, port))
            return so
        except:
            print("Couldn't connect to " + str(ip))

    def registerAllFiles(self, servers, port):
        files = client.findAllFiles()
        indexport = client.selectServer(servers)  # Connect to a random indexing server
        sock = client.socketConnect(indexip, int(indexport))
        if sock:
            for f in files:
                f.replace(" ", "")
                client.register(f, sock, port)
                print(sock.recv(4096).decode())
                sock = client.socketConnect(indexip, int(indexport))  # Reset the socket
            sock.shutdown(socket.SHUT_WR)

    def register(self, filename, sock, port):
        sock.send(("register " + filename + " " + str(port)).encode())

    def findAllFiles(self):
        files = []
        for (dirpath, dirnames, filenames) in walk("."):  # parse all directories and files
            files.extend(filenames)
            break   # break after one iteration to remain at the same level
        if "Client.py" in files:
            files.remove("Client.py")
        if "Server.py" in files:
            files.remove("Server.py")
        return files

    def lookup(self, filename, sock, port):
        sock.send(("lookup " + filename + " " + str(port)).encode())
        return sock.recv(4096).decode()

    def decentralizedLookup(self, filename, servers):
        result = ""
        for indexport in servers:
            sock = client.socketConnect(indexip, int(indexport))
            if sock:
                result = client.lookup(filename, sock, server.port)
                sock.shutdown(socket.SHUT_WR)
                if "404 - No peer has registered this file" not in result:  # keeps the decentralization transparent by
                                                                            # only showing one result message
                    print(result)
                    break
        if "404 - No peer has registered this file" in result:
            print(result)

    def getFile(self, filename, sock):
        tempfilename = filename
        while path.isfile(tempfilename):
            tempfilename += "_"  # Avoiding files with the same name
        f = open(tempfilename, 'w')
        sock.send(("get " + str(filename)).encode())
        print("Receiving file data")
        fdata = sock.recv(4096).decode()
        while (fdata):
            print("Receiving file data")
            f.write(fdata)
            fdata = sock.recv(4096).decode()
        f.close()
        print("\nDisplay file \'" + filename + "\'\n")  # print to stdout instead of opening
        print(sock.recv(4096).decode())


class Server:
    def __init__(self):
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = 12345  # This port is how a client will connect
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def giveFile(self, filename, sock):
        f = open(filename, 'r')
        fdata = f.read(4096)
        while (fdata):
            sock.send(fdata.encode())
            fdata = f.read(4096)
        f.close()
        sock.shutdown(socket.SHUT_WR)

    def threadedListening(self):
        self.sock.listen(5)  # Limit to 5 concurrent connections
        lock = threading.Lock()
        lock.acquire()
        print("\n[LISTENING PROCESS]\nServer socket listening...\n")
        lock.release()
        while 1:
            client, ip = self.sock.accept()
            client.settimeout(120)  # Terminate after 2min of inactivity
            threading._start_new_thread(self.Listen, (client, ip, lock))

    def Listen(self, client, ip, lock):
        data = client.recv(4096).decode()
        infos = data.split(" ")
        if infos[0] == "get":
            lock.acquire()
            self.giveFile(infos[1], client)
            lock.release()


if __name__ == "__main__":
    cfg = open("../../Indexcfg", "r")
    servers = cfg.read().strip().split("|")
    cfg.close()
    server = Server()
    client = Client()
    listenerProcess = Process(target=server.threadedListening).start()
    indexip = "127.0.1.1"  # Hardcoded for simplicity but in a multi-node setting, this will change
    while True:
        userinput = input(
            "Enter commmand:\n"
            " \"get\" to download a file.\n"
            " \"register\" to index one of your files\n"
            " \"lookup\" to query for a desired file location\n"
            " \"test\" to enter the performance testing mode\n"
            " \"exit\" to quit the program\n"
            "or let the program run for the server to listen\n")
        if userinput == "get":
            userinput = input("Filename ?\n")
            ip = "127.0.1.1"
            port = input("File host port ?\n")
            sock = client.socketConnect(ip, int(port))
            if sock:
                client.getFile(userinput, sock)
                print(sock.recv(4096).decode())
                sock.shutdown(socket.SHUT_WR)
        elif userinput == 'register':
            client.registerAllFiles(servers, server.port)
        elif userinput == 'lookup':
            filename = input("Filename ?\n").replace(" ", "")
            client.decentralizedLookup(filename, servers)
        elif userinput == "exit":
            print("warning, this will also terminate the server process\n")
            input = input("Are you sure ? (y/n)\n")
            if input == "y":
                sys.exit()
        elif userinput == "test":
            N = input("How many requests ?\n")
            response = input("Multithreading test ? (y/n)\n")
            if response == "n":
                userinput = input("Test which command ? lookup/register/get\n")
                if (userinput == "lookup")|(userinput == "get")|(userinput == "register"):
                    print("Beginning of test :\n")
                    result = client.testAverageReqTime(servers, int(N), userinput, server.port)
                    print("[The average request took " + str(result) + " seconds]")
            if response == "y":
                userinput = input("Test which command ? lookup/register/get\n")
                if (userinput == "lookup")|(userinput == "get")|(userinput == "register"):
                    client.testMulti(servers, int(N), userinput, server.port)

        else:
            print("Incorrect command.\n")
