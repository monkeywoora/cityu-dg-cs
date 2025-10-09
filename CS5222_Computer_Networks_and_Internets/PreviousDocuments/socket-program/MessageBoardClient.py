"""
@Author: nobody.su
@Date: 2024/11/13
请勿直接copy提交 有可能被判剽窃..
"""

import socket
import sys

FORMAT = 'utf-8'
BUFFER = 4096

class MessageBoardClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client_socket.connect((self.server_ip, self.server_port))
        except socket.error as e:
            print(f"Error connecting to server: {e}")
            sys.exit()

    '''
    个人认为，严格来讲，
    如果单次发送的超过4096字节，服务端和客户端发送和接收方法都应该对字符串分批，如4097=4096+1。否则会影响下一个发送接收回合
    这里默认服务端代码是不可修改的，所以暂不修改客户端，当作已知条件单次输入不超过4096个字符
    '''
    def encode_sendmsg(self, str):
        """
        向服务器发送命令，凑够一个字节流，因为服务器每次recv是一个字节流(BUFFER)
        :param str:
        :param client_socket: 套接字对象
        :param command: 要发送的命令字符串
        """
        try:
            byte_str = bytes(str, encoding=FORMAT)
            if len(byte_str) < BUFFER:
                byte_str += b' ' * (BUFFER-len(byte_str))
            self.client_socket.send(byte_str)
        except socket.error as e:
            print(f"CLIENT:Error sending command: {e}")

    def decode_recvmsg(self):
        #程序执行到这一行时，如果没有足够的数据到达，代码会暂停在这里，直到接收到足够的数据或者连接关闭
        recv_msg = self.client_socket.recv(BUFFER)
        # b'GET' 网络通信传输的是字节流，而不是直接的字符串。
        # 当服务器接收到字节数据后，需要将其解码为字符串才能进行进一步的处理
        # 等价于str.decode('utf-8')
        return str(recv_msg, encoding='utf-8')

    def deal_post_command(self):
        print("CLIENT:Enter your message (type '#' on a new line to finish):")
        while True:
            line = input()
            self.encode_sendmsg(line)
            if line == "#":
                break
        print('SERVER:' + self.decode_recvmsg())

    def det_get_command(self):
        first_tip = self.decode_recvmsg()
        print(first_tip)
        while True:
            per_msg = self.decode_recvmsg()
            if per_msg == '#':
                break
            print(per_msg)
        print("SERVER:\"GET\" done")


    def deal_delete_command(self):
        print("CLIENT:Enter your delete ids line by line, type '#' on a new line to finish(Check id by GET):")
        while True:
            line = input()
            self.encode_sendmsg(line)
            if line == "#":
                break
        print('SERVER:' + self.decode_recvmsg())

    #main interact
    def handle_command(self):
        while True:
            command = input("CLIENT:Enter command (POST, GET, DELETE, QUIT): ").upper()
            self.encode_sendmsg(command)
            if command == 'GET':
                self.det_get_command()
            elif command == "POST":
                self.deal_post_command()
            elif command == "DELETE":
                self.deal_delete_command()
            elif command == 'QUIT':
                response = self.decode_recvmsg()
                if command == "QUIT" and response.strip() == "OK":
                    self.client_socket.close()
                    sys.exit(0)
            else:
                print("CLIENT:Invalid command. Try again.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python message_board_client.py <Server IP> <Server Port>")
        sys.exit()

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])
    #DEBUG:
    # server_ip = '127.0.0.1'
    # server_port = 16111
    client = MessageBoardClient(server_ip, server_port)
    client.connect()
    client.handle_command()