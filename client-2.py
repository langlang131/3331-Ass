#! /usr/bin/env python3

'''
COMP3331/9331 Computer Networks and Applications
Programming Tutorial

Usage:      python3 client.py <server_port> <username> <wordlist>
Example:    python3 client.py 54321 comp3331 rockyou10k-1.txt

The server is expected to be running on the same machine as the client, and the
server should be started before the client is run.

Standard libraries included below that you may find helpful to complete the task:
[socket]: https://docs.python.org/3/library/socket.html
'''

import argparse
import hashlib
import socket

BUFFER_SIZE = 1024

def main():
    """The main function that parses the command line arguments and starts the client."""
    parser = argparse.ArgumentParser()
    parser.add_argument('server_port', type=int, help='TCP port of the server')
    parser.add_argument('username', help='username of the account to authenticate')
    parser.add_argument('wordlist', help='wordlist file')
    args = parser.parse_args()

    authentication_client(args.server_port, args.username, args.wordlist)

def authentication_client(server_port: int, username: str, wordlist: str) -> None:
    '''Connects to the server and sends authentication requests for the given 
       username, trialling each of the passwords in the wordlist file.
    
    Args:
        server_port (int): The TCP port of the server.
        username (str): The username of the account to authenticate.
        wordlist (str): The path to the wordlist file.
    '''
    print(f'Username: {username}')
    authenticated = False

    with open(wordlist, 'r', encoding='utf-8') as file:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(('localhost', server_port))

            for line in file:
                password = line.strip()
                password_hash = hashlib.sha1(password.encode()).hexdigest()

                # We use carriage return to overwrite the previous password
                # attempt on the terminal.
                display = f'Password: {password}'
                print(display, end='\r')

                request = f'{username}\n{password_hash}\n'
                client_socket.send(request.encode())
                response = client_socket.recv(BUFFER_SIZE).decode()

                if response == 'authorised':
                    print(f'\n{response}')
                    authenticated = True
                    break

                # Clear the previous password attempt from the terminal.
                print(' ' * len(display), end='\r', flush=True)

    if not authenticated:
        print(f'Password not found in wordlist: {wordlist}')

if __name__ == '__main__':
    main()
