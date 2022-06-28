import socket
import threading
import queue

HOST = 'localhost'
PORT = 9999

messages = queue.Queue()
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

def receive():
    while True:
        try:
            message, address = server.recvfrom(1024)
            messages.put((message, address))
        except:
            pass


def broadcast():
    while True:
        while not messages.empty():
            message, address = messages.get(1024)
            print(message.decode())
            if address not in clients:
                clients.append(address)
            for client in clients:
                try:
                    if message.decode().startswith("SIGNUP_TAG:"):
                        nick = message.decode()[message.decode().index(":")+1:]
                        server.sendto(f'{nick} joined to the party!'.encode(), client)
                    else:
                        server.sendto(message, client)
                except:
                    clients.remove(client)


thread_receive = threading.Thread(target=receive)
thread_broadcast = threading.Thread(target=broadcast)

thread_receive.start()
thread_broadcast.start()
