import threading
import socket


HOST = 'localhost'
PORT = 9982


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            
            if msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    nick_to_kick = msg.decode('ascii')[5:]
                    kick_user(nick_to_kick)
                else:
                    client.send("Command was redused!".encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    nick_to_ban = msg.decode('ascii')[4:]
                    kick_user(nick_to_ban)
                    # ban_user(nick_to_ban)
                    with open("tcp_banned.txt", 'a') as f:
                        f.write(f'{nick_to_ban}\n')
                    print (f'{nick_to_ban} was banned!')
                else:
                    client.send("Command was redused!".encode('ascii'))
            else:
                broadcast(message)
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast(f"{nickname} has left the conversation.".encode('ascii'))
                nicknames.remove(nickname)
                break


def receive():
    while True:
        client, address = server.accept()
        print (f"Connected with: {str(address)}")
        client.send("NICK".encode('ascii'))
        nickname = client.recv(1024).decode('ascii')

        with open("tcp_banned.txt", "r") as f:
            bans = f.readlines()
        
        if nickname+'\n' in bans:
            client.send("BAN".encode('ascii'))
            client.close()
            continue

        if nickname == "admin":
            client.send("PASSWD:".encode('ascii'))
            passwd = client.recv(1024).decode('ascii')
            if password != "adminpass":
                client.send("REFUSE".encode('ascii'))
                client.close()
                continue

        nicknames.append(nickname)
        clients.append(client)
        print(f"Nickname of the client is: {str(nickname)}!")
        broadcast(f"{nickname} arrived!".encode('ascii'))
        client.send("\nConnected to the server!".encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


def kick_user(uname):
    if uname in nicknames:
        uname_index = nicknames.index(uname)
        client_to_kick = clients[uname_index]
        clients.remove(client_to_kick)
        client_to_kick.send("You're kicked by the admin!".encode('ascii'))
        client_to_kick.close()
        nicknames.remove(uname)
        broadcast(f'{uname} was kicked by the admin'.encode('ascii'))

print("SERCER is running! >>> listening started...")
receive()
