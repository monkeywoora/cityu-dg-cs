import socket 

# Define the server IP and port
server_ip = '127.0.0.1'
server_port = 16111 
# Create a socket to connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

try: 
    # Task 2: Initiate the connection request
    client_socket.connect((server_ip, server_port))
    print("IP Address:", server_ip, "Port Number:", server_port)
    print ("Connect status: OK") 

    while True:
    # Task 3: Send command to the server
        command = input("Enter command (POST, DELETE, GET, QUIT, JUMP): ")
        client_socket.send(command.encode())
        if command == "POST":
            print("Enter text line by line, end with '#' on a new line:")
            while True:
                text = input()
                client_socket.send((text +'\n').encode())
                if text == '#':
                    break
            while True:
                message = client_socket.recv(4096).decode()
                if message == '#':
                    break
                print(message)
        elif command == 'DELETE':
        # Task 3: delete the command to the server
            print("Enter number line by line, end with '#' on a new line:")
            while True:
                text = input()
                client_socket.send((text +'\n').encode())
                if text == '#':
                    break
            while True:
                message = client_socket.recv(4096).decode()
                if message == '#':
                    break
                print(message)
        elif command == 'JUMP':
        # Task 4: query the command to the server
            print("Enter ID number line by line, end with '#' on a new line:")
            while True:
                text = input()
                client_socket.send((text +'\n').encode())    
                if text == '#':
                    break
            while True:
                message = client_socket.recv(4096).decode()
                if message == '#':
                    break
                print(message)
        elif command == 'GET':
        # Task 5: Receive and display messages from the server
            print("Messages from the server:")
            while True:
                message = client_socket.recv(4096).decode()
                if message == '#':
                    break
                print(message)
            print('#')
        elif command == 'QUIT':                                                                                                             
            # Task 6: Close the socket
            while True:
                message = client_socket.recv(4096).decode()
                if message == '#':
                    break
                print(message) 
            client_socket.close() 
            print("Now the Connection is closed.")
            print("If you would like to exit this program,")
            print("please wait to quit.")
            exit(0)
        else:
            response = client_socket.recv(4096).decode()
            if response == 'ERROR - Command not understood':
                print(response)
            else:
                print("OK") 
except ConnectionRefusedError:
    print ("Error: Connection not estabashed. Check the server address and port.")
finally:
        client_socket.close() 
        exit(0)
