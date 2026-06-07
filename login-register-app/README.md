# Login & Register App

A **client-server** application with a graphical interface, where users can register
and log in. The client (Tkinter GUI) talks to a Python server over **sockets** using
a custom text protocol.

## Features

- Tkinter GUI with login, registration and language screens
- Client-server communication over TCP sockets
- Custom message protocol (see `chatlib.py`)
- Users stored in `server/data/users.json`
- Show/hide password toggle
- Connection-error handling and confirmation dialogs

## How to run

Open **two terminals**.

**1. Start the server:**
```bash
cd server
pip install colorama
python personal_details_server.py
```

**2. Start the client:**
```bash
pip install pillow
python app.py
```

The client connects to `127.0.0.1:6996` by default (configurable at the top of `app.py`).

> Note: `users.json` ships with a demo user (`liron` / `123`) for testing.
