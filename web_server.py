#!/usr/bin/env python3
import select
import sys
import socket
import re
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: web_server.py PORT")
    sys.exit()

host = '127.0.0.1'
port = int(sys.argv[1])
KEEP_ALIVE_TIMEOUT = 20  # seconds

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.listen()
    while True:
        conn, addr = s.accept()
        conn.setblocking(0)
        with conn:
            print(f"Connected by {addr}")
            alive = True
            while alive:
                # Use select to check if data is ready to be received
                ready = select.select([conn], [], [], KEEP_ALIVE_TIMEOUT)
                if ready[0]:
                    data = conn.recv(1024)
                else:
                    break

                if not data:
                    print("Received empty packet - closing connection.")
                    break

                print(f"Received: {data[:20]}")
                if not re.match(b'GET .* HTTP/1.1', data):
                    print("Not a GET request.")
                    break
                file = re.findall(b'GET (.*) HTTP/1.1', data)[0][1:].decode()
                if file == '':
                    file = 'index.html'
                if not Path(file).exists():
                    # Error 404
                    print(f"File {file} not found.")
                    status = b"404 Not Found"
                    content = b"Page Not Found!"
                else:
                    status = b"200 OK"
                    with open(file, 'rb') as f:
                        content = f.read()
                # Create Header
                header = b"HTTP/1.1 " + status + b"\r\n"
                header += b"Content-Length: " + str(len(content)).encode() + b"\r\n"
                header += b"Connection: keep-alive\r\n"
                header += b"Keep-Alive: timeout=" + str(KEEP_ALIVE_TIMEOUT).encode() + b", max=100\r\n"
                header += b"\r\n"
                # Create Message
                msg = header + content
                # Send response
                conn.sendall(msg)
                # Determine if connection should be closed
                if re.search(b'Connection: close', data):
                    alive = False
                    print("Client requested connection close.")
