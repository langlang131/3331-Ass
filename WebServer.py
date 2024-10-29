import socket
import os
import argparse


def handle_request(client_socket):
    while True:
        request = client_socket.recv(1024).decode()
        print(f"Request: {request}")

        if not request:  
            client_socket.close()
            return

        lines = request.splitlines()
        if len(lines) > 0:
            file_path = lines[0].split()[1][1:] 

            if os.path.exists(file_path) and os.path.isfile(file_path):
                if file_path.endswith('.png'):
                    content_type = 'image/png'
                elif file_path.endswith('.html'):
                    content_type = 'text/html'
                    
                else:
                    content_type = 'application/octet-stream'  


                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    response = (f"HTTP/1.1 200 OK\r\n"
                                f"Content-Type: {content_type}\r\n"
                                f"Connection: keep-alive\r\n" 
                                f"Content-Length: {len(content)}\r\n"  
                                f"\r\n").encode() + content
                except Exception as e:
                    response = b"HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n<html><body><h1>500 Internal Server Error</h1></body></html>"
            else:
                error_message = "<html><body><h1>404 Not Found</h1><p>The requested resource could not be found on this server.</p></body></html>"
                response = (f"HTTP/1.1 404 Not Found\r\n"
                            f"Content-Type: text/html\r\n"
                            f"Content-Length: {len(error_message)}\r\n"
                            f"Connection: keep-alive\r\n"  
                            f"\r\n").encode() + error_message.encode()
        else:
            response = b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\n\r\n<html><body><h1>400 Bad Request</h1></body></html>"

        client_socket.sendall(response)  
        
        # 不关闭 socket!!

def run_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ('Socket created')
    server_socket.bind(('127.0.0.1', port))
    server_socket.listen(5)

    print(f"Server is listening on port {port}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")
        handle_request(conn)  

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    run_server(args.port)
