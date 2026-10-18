import socket
import sys
import threading

from chat_logger import get_timestamp

HOST = "localhost"
PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind to port 0 to let the OS assign an available ephemeral port safely
client.bind((HOST, 0))

nick = input("Enter a nickname: ").strip()
while not nick:
    nick = input("Nickname cannot be empty. Enter a nickname: ").strip()


def receive():
    while True:
        try:
            message, _ = client.recvfrom(1024)
            print(message.decode('utf-8', errors='replace').rstrip())
        except OSError:
            break


def main():
    crecv_thread = threading.Thread(target=receive, daemon=True)
    crecv_thread.start()

    client.sendto(f"SIGNUP_TAG:{nick}".encode(), (HOST, PORT))
    print(f"[{get_timestamp()}] Type '/quit' or '!q' to quit.")

    while True:
        try:
            message = input("")
        except (KeyboardInterrupt, EOFError):
            message = "!q"

        if not message.strip():
            continue

        if message.lower() in ("!q", "/quit", "quit", "exit"):
            try:
                client.sendto(f"QUIT_TAG:{nick}".encode(), (HOST, PORT))
            except OSError:
                pass
            print(f"[{get_timestamp()}] You left the conversation.")
            break

        try:
            client.sendto(f'[{get_timestamp()}] {nick}: {message}'.encode(), (HOST, PORT))
        except OSError as e:
            print(f"Error sending message: {e}", file=sys.stderr)
            break

    client.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
