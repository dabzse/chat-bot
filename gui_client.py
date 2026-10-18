import socket
import sys
import threading
import tkinter as tk
import tkinter.scrolledtext
from tkinter import simpledialog

from chat_logger import get_timestamp

HOST = 'localhost'
PORT = 9092


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.sock.connect((self.host, self.port))
        except OSError as e:
            print(f"[{get_timestamp()}] Could not connect to server at {self.host}:{self.port}: {e}", file=sys.stderr)
            sys.exit(1)

        msg = tk.Tk()
        msg.withdraw()
        self.nickname = simpledialog.askstring("Nickname", "Please, choose a nickname.", parent=msg)
        msg.destroy()

        if not self.nickname:
            print(f"[{get_timestamp()}] Nickname is required. Exiting...", file=sys.stderr)
            self.sock.close()
            sys.exit(0)

        self.gui_done = False
        self.running = True

        receive_thread = threading.Thread(target=self.receive, daemon=True)
        receive_thread.start()

        self.gui_loop()

    def gui_loop(self):
        self.win = tk.Tk()
        self.win.configure(bg='lightblue')
        self.win.title("ChatAPP GUI: @dabzse")

        self.chat_label = tk.Label(self.win, text='TkInter GUI ChatAPP: @dabzse', bg='lightgray')
        self.chat_label.config(font=('FreeSans', 13))
        self.chat_label.pack(padx=21, pady=7)

        self.help_label = tk.Label(
            self.win,
            text="Type '/quit' or '!q' or click Quit to leave the conversation.",
            bg='lightblue',
            fg='#333333',
            font=('FreeSans', 10)
        )
        self.help_label.pack(padx=21, pady=(0, 7))

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=21, pady=7)
        self.text_area.config(state='disabled')

        self.msg_label = tk.Label(self.win, text='Message', bg='lightgray')
        self.msg_label.config(font=('FreeSans', 13))
        self.msg_label.pack(padx=21, pady=7)

        self.input_area = tk.Text(self.win, height=4)
        self.input_area.pack(padx=21, pady=7)

        btn_frame = tk.Frame(self.win, bg='lightblue')
        btn_frame.pack(padx=21, pady=7)

        self.send_button = tk.Button(btn_frame, text='Send', command=self.write)
        self.send_button.config(font=('FreeSans', 13))
        self.send_button.pack(side=tk.LEFT, padx=7)

        self.quit_button = tk.Button(btn_frame, text='Quit', command=self.stop)
        self.quit_button.config(font=('FreeSans', 13))
        self.quit_button.pack(side=tk.LEFT, padx=7)

        self.gui_done = True
        self._display_message(f"[{get_timestamp()}] Type '/quit' or '!q' to quit.\n")
        self.win.protocol('WM_DELETE_WINDOW', self.stop)
        self.win.mainloop()

    def write(self):
        msg_text = self.input_area.get('1.0', 'end').strip()
        if not msg_text:
            return

        if msg_text.lower() in ('/quit', '!q', 'quit', 'exit'):
            self.stop()
            return

        timestamp = get_timestamp()
        message = f"[{timestamp}] {self.nickname}: {msg_text}\n"
        try:
            self.sock.send(message.encode())
        except OSError:
            pass
        self.input_area.delete('1.0', 'end')

    def stop(self):
        if not self.running:
            return
        self.running = False
        leave_msg = f"[{get_timestamp()}] You left the conversation.\n"
        self._display_message(leave_msg)
        try:
            self.sock.close()
        except OSError:
            pass
        try:
            self.win.destroy()
        except tk.TclError:
            pass
        sys.exit(0)

    def _display_message(self, message):
        if self.gui_done:
            self.text_area.config(state='normal')
            self.text_area.insert('end', message)
            self.text_area.yview('end')
            self.text_area.config(state='disabled')

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8', errors='replace')
                if not message:
                    print(f"[{get_timestamp()}] Server closed the connection.")
                    break
                if message == 'NICK':
                    self.sock.send(self.nickname.encode())
                else:
                    self._display_message(message)
            except OSError:
                if self.running:
                    print(f"[{get_timestamp()}] Connection lost.", file=sys.stderr)
                break
        if self.running:
            self.stop()


if __name__ == '__main__':
    Client(HOST, PORT)
