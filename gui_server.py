import socket
import threading

from chat_logger import ChatLogger, get_timestamp

HOST = 'localhost'
PORT = 9092

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


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            decoded = message.decode('utf-8', errors='replace').strip()
            if not decoded.startswith('['):
                decoded = f"[{get_timestamp()}] {decoded}"
            broadcast(decoded + '\n')
        except OSError:
            break

    if client in clients:
        index = clients.index(client)
        clients.remove(client)
        client.close()
        nickname = nicknames.pop(index)
        broadcast(f"[{get_timestamp()}] {nickname} left the conversation.\n")


def receive():
    while True:
        try:
            client, address = server.accept()
            logger.log(f"[{get_timestamp()}] Connected with {address}!")

            client.send(b"NICK")
            nickname = client.recv(1024).decode('utf-8', errors='replace').strip()
            if not nickname:
                client.close()
                continue

            nicknames.append(nickname)
            clients.append(client)
            logger.log(f"[{get_timestamp()}] Nickname of this client is: {nickname}")
            broadcast(f"[{get_timestamp()}] {nickname} joined the conversation.\n")
            client.send(f"\n[{get_timestamp()}] Successfully connected to the server!\n".encode())

            thread = threading.Thread(target=handle, args=(client,), daemon=True)
            thread.start()
        except KeyboardInterrupt:
            logger.log(f"\n[{get_timestamp()}] Server shutting down...")
            server.close()
            break
        except OSError as e:
            logger.log(f"[{get_timestamp()}] Connection error: {e}")


if __name__ == '__main__':
    logger.log(f"[{get_timestamp()}] >>> GUI SERVER is running on {HOST}:{PORT}...")
    try:
        receive()
    except KeyboardInterrupt:
        logger.log(f"\n[{get_timestamp()}] Server stopped.")
