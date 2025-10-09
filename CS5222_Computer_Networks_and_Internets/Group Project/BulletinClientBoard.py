import socket
import os
import sys
import time
import struct

SENDING_COOLDOWN = 0.1 # in seconds
BUFFER_SIZE = 4096
PROMPT_LEN = 60
FILE_SIZE_LIMIT = 256 # in bytes; you may change this value

def init_socket():
    print(' Initialize socket '.center(PROMPT_LEN, '='))
    ip = input('input IP address : ')
    port = input('input port number: ')
    return ip, port

def connect_socket(ip, port):
    '''
    Try to establish a socket connection to the server
    Exception handling:
        wrong ip address or port number
        time out
        cannot send message to server
    '''
    try:
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _socket.settimeout(5)
        _socket.connect((ip, int(port))) # port number must be integer within 0-65535
        return _socket
    except (OSError, ValueError, OverflowError, TimeoutError):
        print('Error: connection is not built, try again')
        return None
    else:
        try:
            _socket.send('hello world'.encode('utf-8'))
            _socket.recv(BUFFER_SIZE)
        except Exception:
            print('Error: connection does not allow sending message, try again')
            return None
        else:
            print(' Input command '.center(PROMPT_LEN, '='))
            return _socket
            
def stripe_string(server_msg):
    '''
    Remove the 'server: ' prefix from the server message
    Exception handling: given string is invalid
    '''
    if server_msg is None or len(server_msg) < 8 or server_msg[:8] != 'server: ':
        return server_msg
    return server_msg[8:]

class BulletinClientBoard:

    ERROR_STR = 'ERROR - Command not understood'
    OK_STR = 'OK'

    def __init__(self, ip, port, _socket):
        self.ip = socket.gethostbyname(ip)
        self.port = port
        self._socket = _socket
    
    def send_string(self, string):
        '''
        Send a string to the server
        '''
        try:
            self._socket.send(string.encode('utf-8'))
            time.sleep(SENDING_COOLDOWN)
            return True
        except Exception:
            return False
    
    def recv(self):
        '''
        Receive a string from the server
        '''
        try:
            return self._socket.recv(BUFFER_SIZE).decode('utf-8')
        except Exception:
            return None
    
    def send_file(self, file_path):
        '''
        Send a file to the server
        Exception handling: file does not exist
        '''
        try:
            if os.path.isfile(file_path):
                if os.path.getsize(file_path) > FILE_SIZE_LIMIT:
                    print('client: ERROR - File size limit exceeded')
                    self._socket.send(b'close')
                    return False
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                file_info = struct.pack('128sl', file_name.encode('utf-8'), file_size)
                self._socket.send(file_info)
                print(f'Transfer file absolute path: {file_path}')
                with open(file_path, 'rb') as f:
                    while True:
                        file_data = f.read(BUFFER_SIZE)
                        if not file_data:
                            break
                        self._socket.send(file_data)
                return True
            else:
                print('client: ERROR - File does not exist')
                self._socket.send(b'close')
                return False
        except Exception:
            return False

    def post_string(self):
        '''
        Implements POST_STRING command
        Receive multiple lines of string from the user and send them to the server
        The message ends after a single line containing only '&'
        Exception handling: server does not receive the message
        '''
        message_cnt = 0
        print(' Content (Type a lone \'&\' to end message) '.center(PROMPT_LEN, '='))
        self.send_string('POST_STRING')
        while True:
            message = input('client: ')
            if len(message) == 0:
                print('client: Empty message will not be sent')
                continue
            message_cnt += 1
            self.send_string(message)
            if message == '&':
                break
        msg = self.recv()
        if msg is None or stripe_string(msg) != 'OK':
            print('---')
            print(f'Cannot send message to (IP address: {self.ip}, port number: {self.port})')
            print('Connect status: ERROR')
            print('Send status: ERROR')
            print('---')
        else:
            print(msg)
            print('---')
            print(f'Sent {message_cnt} messages to (IP address: {self.ip}, port number: {self.port})')
            print('Connect status: OK')
            print('Send status: OK')
            print('---')
        print(' Next command '.center(PROMPT_LEN, '='))
    
    def post_file(self):
        '''
        Implements POST_FILE command
        Read file path from the user and send the file to the server
        Exception handling:
            server does not receive the file
            file does not exist
        '''
        self.send_string('POST_FILE')
        print(self.recv())
        try:
            file_path = input('client: ')
        except KeyboardInterrupt: # If user press Ctrl+C, cancel file transfer
            print('client: File transfer canceled')
            self._socket.send(b'close')
            print(self.recv())
            print(' Next command '.center(PROMPT_LEN, '='))
            return
        if self.send_file(file_path):
            print(self.recv())
            print('---')
            print(f'Sent file to (IP address: {self.ip}, port number: {self.port})')
            print('Connect status: OK')
            print('Send status: OK')
            print('---')
        else:
            print(self.recv())
            print('---')
            print(f'Cannot send file to (IP address: {self.ip}, port number: {self.port})')
            print('Connect status: ERROR')
            print('Send status: ERROR')
            print('---')
        print(' Next command '.center(PROMPT_LEN, '='))
    
    def get(self):
        '''
        Implements GET command
        Receive multiple lines of string from the server and print them
        The message ends after a single line containing only '&'
        Exception handling: server does not send the message
        '''
        self.send_string('GET')
        msg = self.recv()
        if msg is None:
            print('---')
            print(f'Cannot receive message from (IP address: {self.ip}, port number: {self.port})')
            print('Connect status: ERROR')
            print('Get status: ERROR')
            print('---')
            print(' Next command '.center(PROMPT_LEN, '='))
            return
        while msg is not None:
            msg = stripe_string(msg)
            print(f'client: {msg}')
            if msg == '&':
                break
            msg = self.recv()
        print('---')
        print(f'Received messages from (IP address: {self.ip}, port number: {self.port})')
        print('Connect status: OK')
        print('Get status: OK')
        print('---')
        print(' Next command '.center(PROMPT_LEN, '='))

    def terminate(self):
        '''
        Implements EXIT command
        Close the socket and exit the program
        '''
        self.send_string('EXIT')
        print(self.recv())
        self._socket.close()
        sys.exit(0)

    def start(self):
        '''
        Main loop of the client
        '''
        print(' Input command '.center(PROMPT_LEN, '='))
        while True:
            try:
                command = input('Input command: ')
                tokens = command.split()
                if len(tokens) == 0:
                    print(f'client: {self.ERROR_STR}')
                    continue
                if tokens[0] == 'POST_STRING':
                    self.post_string()
                elif tokens[0] == 'POST_FILE':
                    self.post_file()
                elif tokens[0] == 'GET':
                    self.get()
                elif tokens[0] == 'EXIT':
                    self.terminate()
                else:
                    self.send_string(command)
                    print(self.recv())
            except KeyboardInterrupt: # If user press Ctrl+C, terminate the connection
                self.terminate()

if __name__ == '__main__':
    client = None
    while client is None:
        ip, port = init_socket()
        _socket = connect_socket(ip, port)
        if _socket is not None:
            client = BulletinClientBoard(ip, port, _socket)
    client.start()
