import socket

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s1.connect(("127.0.1.1", 12341))
    s.connect(("127.0.1.1", 12341))
    s.send("test lol".encode())
    s1.send("test lol".encode())
    print(s.recv(4096).decode())
    print(s.recv(4096).decode())
except socket.error as e:
    print(str(e))