import threading
import socket


HOST = 'localhost'
PORT = 9982

nickname = input("Choose a nickname: ")
if nickname == 'admin':
    password = input("Enter your password: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

stop_thread = False

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break

        try:
            message = client.recv(1024).decode('ascii')
            if message == "NICK":
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')
                if next_message == "PASS":
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == "REFUSE":
                        print("Connection was refused.")
                        stop_thread = True
                elif next_message == "BAN":
                    print("Connection refused because of ban!".encode('ascii'))
                    client.close()

            else:
                print(message)
        except:
            print("Something went wrong.")
            client.close()
            break


def write():
    while True:
        global stop_thread
        if stop_thread:
            break

        message = f'{nickname}: {input("")}'
        
        if message[len(nickname)+2].startswith('/'):
            if nickname == 'admin':
                if message[len(nickname)+2].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('ascii'))
                elif message[len(nickname)+2].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('ascii'))
            else:
                print("Only admin can use commands.")
        else:
            client.send(message.encode('ascii'))


receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
