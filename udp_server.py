import queue
import socket
import threading

from chat_logger import ChatLogger, get_timestamp

HOST = 'localhost'
PORT = 9999

logger = ChatLogger(__file__)

messages = queue.Queue()
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))


def receive():
    while True:
        try:
            message, address = server.recvfrom(1024)
            messages.put((message, address))
        except OSError:
            break


def _handle_signup(address, decoded):
    if address not in clients:
        clients.append(address)
    nick = decoded.split(":", 1)[1]
    return f"[{get_timestamp()}] {nick} joined the conversation."


def _handle_quit(address, decoded):
    nick = decoded.split(":", 1)[1]
    if address in clients:
        clients.remove(address)
    return f"[{get_timestamp()}] {nick} left the conversation."


def _handle_chat_message(address, decoded):
    if address not in clients:
        clients.append(address)
    if not decoded.startswith('['):
        return f"[{get_timestamp()}] {decoded}"
    return decoded


def _format_message(address, decoded):
    if decoded.startswith("SIGNUP_TAG:"):
        return _handle_signup(address, decoded)
    if decoded.startswith("QUIT_TAG:"):
        return _handle_quit(address, decoded)
    return _handle_chat_message(address, decoded)


def _send_to_clients(outgoing_bytes):
    for client in clients.copy():
        try:
            server.sendto(outgoing_bytes, client)
        except OSError:
            if client in clients:
                clients.remove(client)


def broadcast():
    while True:
        message, address = messages.get()
        decoded = message.decode('utf-8', errors='replace').strip()
        outgoing_text = _format_message(address, decoded)
        logger.log(outgoing_text)
        _send_to_clients(outgoing_text.encode())


if __name__ == '__main__':
    logger.log(f"[{get_timestamp()}] >>> UDP SERVER is running on {HOST}:{PORT}...")
    thread_receive = threading.Thread(target=receive, daemon=True)
    thread_broadcast = threading.Thread(target=broadcast, daemon=True)

    thread_receive.start()
    thread_broadcast.start()

    try:
        thread_receive.join()
    except KeyboardInterrupt:
        logger.log(f"\n[{get_timestamp()}] Shutting down UDP server...")
        server.close()
