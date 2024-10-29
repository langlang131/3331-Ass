#! /usr/bin/env python3

'''
COMP3331/9331 Computer Networks and Applications
Programming Tutorial

Usage:      python3 server.py <server_port> <accounts_file>
Example:    python3 server.py 54321 accounts.tsv

The server is expected to be running on the same machine as the client, and the
server should be started before the client is run.

Note: There are many different ways to implement the server, and the solution
below is just one possible way.  There are also many ways to improve the
robustness and efficiency of the server, and to add additional features.  This
solution is designed to be simple and easy to understand, and to demonstrate the
basic concepts of a server that handles multiple clients concurrently.

Standard libraries included below that you may find helpful to complete the task:
[socket]: https://docs.python.org/3/library/socket.html
[threading]: https://docs.python.org/3/library/threading.html
[time]: https://docs.python.org/3/library/time.html
'''

import argparse
from pathlib import Path
import socket
import sys
import threading
import time

def main():
    '''The main function that initialises the server and starts it running.'''
    parser = argparse.ArgumentParser()
    parser.add_argument('server_port', type=int, help='TCP port of the server')
    parser.add_argument('accounts_file', help='tab separated file containing account information')
    args = parser.parse_args()

    server = Server(args.server_port, args.accounts_file)
    server.run()

class Server:
    '''
    The server class that listens for TCP connection requests, and for each, 
    spawns a thread to receive and respond to authentication requests.
    '''
    RATE_LIMIT = 0.1 # Rate limit for each client in seconds.
    BUFFER_SIZE = 1024 # Size of the buffer for receiving messages.

    def __init__(self, server_port: int, accounts_file: str):
        '''Initialise the server with the specified port and accounts file.

        Args:
            server_port (int): The TCP port to listen on.
            accounts_file (str): Path to tab-separated file of username-hashed  
              password pairs.
        '''
        self.server_port = server_port
        self.accounts = {}
        self.load_accounts(accounts_file)
        self.is_alive = False
        self.num_active_clients = 0

    def load_accounts(self, accounts_file: str) -> None:
        '''Load the account information from the specified file.

        Args:
            accounts_file (str): Path to tab-separated file of username-hashed  
              password pairs.
        '''
        accounts_file_path = Path(accounts_file)

        if not accounts_file_path.is_file():
            sys.exit(f'Error: {accounts_file} does not exist.')

        with accounts_file_path.open(encoding='utf-8') as f:
            for line in f:
                split_line = line.split()

                if len(split_line) != 2:
                    continue

                username, password_hash = split_line
                self.accounts[username] = password_hash

    def is_authorised(self, username: str, password_hash: str) -> bool:
        '''Check if the specified username and password hash are authorised.

        Args:
            username (str): The username of the account.
            password_hash (str): The hashed password of the account.

        Returns:
            bool: True if the username and password hash are authorised, False 
                otherwise.
        '''
        return username in self.accounts and self.accounts[username] == password_hash

    def run(self):
        '''The main server loop, where the server listens for incoming requests.'''

        try:
            # Create a TCP socket and bind it to the specified port.
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as welcome_socket:
                welcome_socket.bind(('localhost', self.server_port))

                # Listen for incoming connections.
                welcome_socket.listen()
                self.is_alive = True

                print(f'Server running on port {self.server_port}...')
                print('Press Ctrl+C to exit.')

                while True:
                    # Accept a new connection.  This will block until a new connection
                    # is received.
                    connection_socket, client_addr = welcome_socket.accept()

                    # We'll increment this count with each new client connection, and
                    # decrement it when a client thread finishes.  This will allow us
                    # shut down more gracefully, by waiting for all client threads to
                    # finish before exiting.
                    self.num_active_clients += 1

                    # Spawn a new thread to handle the client connection, then
                    # loop back to accept the next connection.
                    child = threading.Thread(target=self.client_thread_handler,
                                             args=(connection_socket, client_addr))
                    child.start()
        except KeyboardInterrupt:
            print('Cleaning up...')

            # Flag the client threads to exit and wait for them to finish.
            self.is_alive = False

            while self.num_active_clients > 0:
                time.sleep(self.RATE_LIMIT)

            print('Server shutdown complete.')

    def client_thread_handler(self, connection_socket, client_addr) -> None:
        '''The handler for each client connection, which processes requests.

        Args:
            connection_socket (socket.socket): The socket for the client connection.
            client_addr (Tuple[str, int]): The (host, port) of the client.
        '''
        # Set the socket to non-blocking mode so we can check intermittently
        # whether the server is still running.  Otherwise, the thread will block
        # indefinitely on recv() and won't be able to check the server status.
        connection_socket.setblocking(False)

        # Convert the client address to a string for logging. (not terribly important)
        client_addr = f'{client_addr[0]}:{client_addr[1]}'

        with connection_socket:
            while self.is_alive:
                try:
                    request = connection_socket.recv(self.BUFFER_SIZE)
                except BlockingIOError:
                    # No data available to read, so we'll just wait a bit and
                    # try again.
                    time.sleep(self.RATE_LIMIT)
                    continue
                except ConnectionResetError:
                    # Client is probably misbehaving (e.g. has forcibly closed
                    # the connection), or thinks we are misbehaving, so we'll
                    # just break the loop and close the connection.
                    break

                # If the client has closed the connection, recv() will return an
                # empty byte string.  We should break the loop in this case.
                if not request:
                    break

                request = request.decode()
                lines = request.split('\n')

                # Just to add a bit of robustness to the request handling.
                lines = [line.strip() for line in lines if len(line.strip()) > 0]

                if len(lines) == 2:
                    username, password_hash = lines
                    print(f'{client_addr}: recv: {username} {password_hash}')

                    response = 'authorised' if self.is_authorised(username, password_hash) \
                        else 'not authorised'
                else:
                    print(f'{client_addr}: recv: {repr(request)}')
                    response = 'bad request'

                print(f'{client_addr}: send: {response}')

                encoded_response = response.encode()
                bytes_sent = connection_socket.send(encoded_response)

                if bytes_sent != len(encoded_response):
                    # We should really do something smarter than this!
                    break

                time.sleep(self.RATE_LIMIT)

        # Decrement this count before the thread finishes, so the server knows
        # when all client threads have finished and it can exit.
        self.num_active_clients -= 1


if __name__ == '__main__':
    main()
