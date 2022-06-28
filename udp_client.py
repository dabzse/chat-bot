import socket
import threading
import random

HOST = "localhost"
PORT = 9999


client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.bind((HOST, random.randint(8000, 9999)))


nick = input("Enter a nickname: ")

def receive():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            print(message.decode())
        except:
            pass


crecv_thread = threading.Thread(target=receive)
crecv_thread.start()

client.sendto(f"SIGNUP_TAG:{nick}".encode(), (HOST, PORT))


while True:
    message = input("")
    if message == "!q":
        exit()
    else:
        client.sendto(f'{nick}: {message}'.encode(), (HOST, PORT))
