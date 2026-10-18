# CHAT + BOT

---

## Overview

This repository contains **4 distinct chat and bot projects**, each identified by its file prefix:

1. **`BOT_*`**: AI-powered intent chatbot using NLTK and TensorFlow / Keras.
2. **`GUI_*`**: Multi-client desktop chat app using TkInter and TCP sockets.
3. **`TCP_*`**: Multi-client terminal chat over TCP with admin authentication, kick, and ban controls.
4. **`UDP_*`**: Lightweight broadcast terminal chat over UDP.

---

### Installation & Requirements

Install dependencies using `requirements.txt`:

```bash
pip install -r requirements.txt
```

> **Note**: For TkInter on Linux (required by `GUI_*`), install your distribution's package:
>
> - **Fedora / RHEL**: `sudo dnf install python3-tkinter`
> - **Debian / Ubuntu**: `sudo apt install python3-tk`

---

### Projects Breakdown

#### 1. BOT_* (AI Intent Chatbot)

- Defined by intents in `bot_intents.json`.
- **Training**: Run `python bot_training.py` to train the neural network and update the model and vocabulary pickles.
- **Running the bot**: Run `python bot_chatbot.py` to start an interactive terminal conversation.
- **Quit command**: Type `/quit` or `!q` to leave the conversation.
- Displays timestamps (`[YYYY-MM-DD HH:MM:SS]`) for user and bot messages.
- Automatically creates daily logs in `logs/bot_*_YYYY-MM-DD.log` (rotates at 00:00:00).

#### 2. GUI_* (TkInter Desktop Chat)

- **Start the server**: `python gui_server.py`
- **Start the client**: `python gui_client.py` (opens GUI window to chat).
- Supports quitting via the "Quit" button or typing `/quit` / `!q` in the message input.
- Displays timestamps (`[YYYY-MM-DD HH:MM:SS]`) and join/leave conversation notices.
- The server automatically creates a daily session log in `logs/gui_server_YYYY-MM-DD.log` (rotates at 00:00:00).

#### 3. TCP_* (TCP Terminal Chat with Admin Commands)

- **Start the server**: `python tcp_server.py`
- **Start a client**: `python tcp_client.py`
- **Quit command**: Type `/quit` or `!q` to leave the conversation cleanly.
- Displays timestamps (`[YYYY-MM-DD HH:MM:SS]`) for all messages and events.
- **Admin**: Connect with nickname `admin` and password `adminpass`.
- **Admin commands**:
  - `/kick <nickname>` - Kicks a user from the room.
  - `/ban <nickname>` - Bans a user and persists their name to `tcp_banned.txt`.
- The server automatically logs all session traffic to daily logs in `logs/tcp_server_YYYY-MM-DD.log` (rotates at 00:00:00).

#### 4. UDP_* (UDP Terminal Chat)

- **Start the server**: `python udp_server.py`
- **Start a client**: `python udp_client.py`
- Uses non-blocking message processing with dynamic OS port allocation.
- **Quit command**: Type `/quit` or `!q` to leave the conversation (notifies peers and server).
- Displays timestamps (`[YYYY-MM-DD HH:MM:SS]`) and join/leave conversation announcements.
- The server automatically logs all session traffic to daily logs in `logs/udp_server_YYYY-MM-DD.log` (rotates at 00:00:00).

---

### Built with

- Python 3.10+
- TensorFlow / Keras
- NLTK
- NumPy
- TkInter

---

Created by @dabzse {{ MNY }}
