import os
import socket
import threading

from chat_logger import ChatLogger, get_timestamp

HOST = 'localhost'
PORT = 9982
BAN_FILE = 'tcp_banned.txt'

logger = ChatLogger(__file__)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []


def broadcast(message):
    if isinstance(message, str):
        encoded = message.encode()
        decoded = message
    else:
        encoded = message
        decoded = message.decode('utf-8', errors='replace')
    logger.log(decoded.strip())
    for client in clients.copy():
        try:
            client.send(encoded)
        except OSError:
            pass


def kick_user(uname):
    if uname in nicknames:
        uname_index = nicknames.index(uname)
        client_to_kick = clients[uname_index]
        try:
            client_to_kick.send(f"[{get_timestamp()}] You were kicked by the admin!\n".encode())
            client_to_kick.close()
        except OSError:
            pass
        clients.remove(client_to_kick)
        nicknames.remove(uname)
        broadcast(f'[{get_timestamp()}] {uname} was kicked by the admin.')


def handle_admin_command(command):
    if command.startswith('KICK '):
        nick_to_kick = command[5:].strip()
        kick_user(nick_to_kick)
    elif command.startswith('BAN '):
        nick_to_ban = command[4:].strip()
        kick_user(nick_to_ban)
        with open(BAN_FILE, 'a', encoding='utf-8') as f:
            f.write(f'{nick_to_ban}\n')
        logger.log(f'[{get_timestamp()}] {nick_to_ban} was banned!')
        broadcast(f'[{get_timestamp()}] {nick_to_ban} was banned by the admin.')


def _remove_client(client):
    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        nickname = nicknames.pop(index)
        broadcast(f"[{get_timestamp()}] {nickname} left the conversation.")


def _handle_admin_action(client, decoded):
    is_admin = client in clients and nicknames[clients.index(client)] == 'admin'
    if is_admin:
        handle_admin_command(decoded)
    else:
        client.send(f"[{get_timestamp()}] Command was refused!\n".encode())


def _process_client_message(client, message):
    decoded = message.decode('utf-8', errors='replace').strip()
    if decoded.startswith(('KICK ', 'BAN ')):
        _handle_admin_action(client, decoded)
        return

    if not decoded.startswith('['):
        decoded = f"[{get_timestamp()}] {decoded}"
    broadcast(decoded)


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            _process_client_message(client, message)
        except OSError:
            break

    _remove_client(client)


def receive():
    while True:
        try:
            client, address = server.accept()
            logger.log(f"[{get_timestamp()}] Connected with: {address}")
            client.send(b"NICK")
            nickname = client.recv(1024).decode('utf-8', errors='replace').strip()

            bans = []
            if os.path.exists(BAN_FILE):
                with open(BAN_FILE, "r", encoding='utf-8') as f:
                    bans = [line.strip() for line in f if line.strip()]

            if nickname in bans:
                client.send(b"BAN")
                client.close()
                continue

            if nickname == "admin":
                client.send(b"PASSWD:")
                passwd = client.recv(1024).decode('utf-8', errors='replace').strip()
                if passwd != "adminpass":
                    client.send(b"REFUSE")
                    client.close()
                    continue

            nicknames.append(nickname)
            clients.append(client)
            logger.log(f"[{get_timestamp()}] Nickname of the client is: {nickname}!")
            broadcast(f"[{get_timestamp()}] {nickname} joined the conversation.")
            client.send(f"\n[{get_timestamp()}] Connected to the server!\n".encode())

            thread = threading.Thread(target=handle, args=(client,), daemon=True)
            thread.start()
        except KeyboardInterrupt:
            logger.log(f"\n[{get_timestamp()}] Shutting down TCP server...")
            server.close()
            break
        except OSError as e:
            logger.log(f"[{get_timestamp()}] Connection error: {e}")


if __name__ == '__main__':
    logger.log(f"[{get_timestamp()}] SERVER is running! >>> listening started on {HOST}:{PORT}...")
    try:
        receive()
    except KeyboardInterrupt:
        logger.log(f"\n[{get_timestamp()}] Server stopped.")
