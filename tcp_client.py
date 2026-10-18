import socket
import sys
import threading

from chat_logger import get_timestamp

HOST = 'localhost'
PORT = 9982

nickname = input("Choose a nickname: ").strip()
while not nickname:
    nickname = input("Nickname cannot be empty. Choose a nickname: ").strip()

password = ""
if nickname == 'admin':
    password = input("Enter your password: ").strip()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((HOST, PORT))
except OSError as e:
    print(f"[{get_timestamp()}] Could not connect to server: {e}", file=sys.stderr)
    sys.exit(1)

stop_thread = False


def _handle_nick_handshake():
    client.send(nickname.encode())
    next_message = client.recv(1024).decode('utf-8', errors='replace')
    if next_message.startswith("PASS"):
        client.send(password.encode())
        resp = client.recv(1024).decode('utf-8', errors='replace')
        if resp == "REFUSE":
            print(f"[{get_timestamp()}] Connection was refused (invalid password).", file=sys.stderr)
            client.close()
            return True
    elif next_message == "BAN":
        print(f"[{get_timestamp()}] Connection refused because of ban!", file=sys.stderr)
        client.close()
        return True
    return False


def _disconnect(reason):
    global stop_thread
    if not stop_thread:
        print(f"[{get_timestamp()}] {reason}")
    stop_thread = True


def _process_message(message):
    if message == "NICK":
        return _handle_nick_handshake()
    print(message.rstrip())
    return False


def receive():
    global stop_thread
    while not stop_thread:
        try:
            message = client.recv(1024).decode('utf-8', errors='replace')
        except OSError:
            _disconnect("Disconnected from server.")
            break

        if not message:
            _disconnect("Server closed the connection.")
            break

        if _process_message(message):
            stop_thread = True
            break


def _send_command(cmd):
    if nickname != 'admin':
        print(f"[{get_timestamp()}] Only admin can use commands.")
        return

    if cmd.startswith('/kick '):
        client.send(f'KICK {cmd[6:].strip()}'.encode())
    elif cmd.startswith('/ban '):
        client.send(f'BAN {cmd[5:].strip()}'.encode())
    else:
        print("Unknown command. Usage: /kick <user> or /ban <user>")


def write():
    global stop_thread
    print(f"[{get_timestamp()}] Type '/quit' or '!q' to quit.")
    while not stop_thread:
        try:
            user_input = input("")
        except (EOFError, KeyboardInterrupt):
            stop_thread = True
            print(f"[{get_timestamp()}] You left the conversation.")
            break

        if not user_input.strip():
            continue

        if user_input.lower() in ('/quit', '!q', 'quit', 'exit'):
            print(f"[{get_timestamp()}] You left the conversation.")
            stop_thread = True
            break

        try:
            if user_input.startswith('/'):
                _send_command(user_input)
            else:
                msg = f'[{get_timestamp()}] {nickname}: {user_input}'
                client.send(msg.encode())
        except OSError:
            stop_thread = True
            break

    try:
        client.close()
    except OSError:
        pass


if __name__ == '__main__':
    receive_thread = threading.Thread(target=receive, daemon=True)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()
    write_thread.join()
    sys.exit(0)
