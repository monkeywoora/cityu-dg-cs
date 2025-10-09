import time
from socketserver import BaseRequestHandler, ThreadingTCPServer
import datetime as dt
from collections import OrderedDict


SENDING_COOLDOWN = 0.3
BUFFER_SIZE = 4096


class EchoHandler(BaseRequestHandler):
    ok_str = 'OK'
    content = ""
    content_idx = 0
    contents = OrderedDict()

    def send_str(self, string):
        self.request.send(bytes(string, encoding='utf-8'))
        time.sleep(SENDING_COOLDOWN)

    def recv_str(self):
        post_msg = self.request.recv(BUFFER_SIZE)
        return str(post_msg, encoding='utf-8')

    def handle(self):
        print('Got connection from', self.client_address)
        while True:
            msg = ""
            try:
                msg = self.recv_str()
            except Exception as e:
                print("Disconnected from", self.client_address)
                pass
            if not msg:
                break
            msg_str = msg.strip().upper()
            print('Message string is:', msg_str)

            if msg_str not in ['POST', 'GET', 'QUIT', 'DELETE']:
                self.send_str('ERROR - Command not understood')
            else:
                command = msg_str
                print('Command is: ', command)
                if command == 'POST':
                    in_post = True
                    while in_post:
                        post_msg_str = self.recv_str().strip()
                        if post_msg_str == "#":
                            in_post = False
                            self.send_str(EchoHandler.ok_str)
                        else:
                            print(f"Added: {post_msg_str}")
                            EchoHandler.content += "\n" + post_msg_str
                    EchoHandler.contents[str(EchoHandler.content_idx).zfill(4)] = {"content": EchoHandler.content.strip(), "datetime": dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
                    EchoHandler.content_idx += 1
                    EchoHandler.content = ""
                elif command == 'GET':
                    self.send_str('Happy Socket Programming')
                    for key in EchoHandler.contents:
                        content = EchoHandler.contents[key]["content"]
                        datetime = EchoHandler.contents[key]["datetime"]
                        self.send_str(f"MESSAGE ID: {key}, RECEIVED DATETIME: {datetime}")
                        for line in content.strip().split("\n"):
                            if line:
                                self.send_str(f"{line}")
                    self.send_str('#')
                elif command == 'DELETE':
                    ids = []
                    in_delete = True
                    while in_delete:
                        delete_msg_str = self.recv_str().strip()
                        if delete_msg_str == "#":
                            in_delete = False
                        else:
                            print(f"Message ID for deletion: {delete_msg_str}")
                            ids.append(delete_msg_str)
                    fail_deletion = False
                    for id in ids:
                        if id not in EchoHandler.contents:
                            fail_deletion = True
                            break
                    if fail_deletion:
                        self.send_str("ERROR - Wrong ID")
                    else:
                        for id in ids:
                            del EchoHandler.contents[id]
                        self.send_str(EchoHandler.ok_str)
                elif command == 'QUIT':
                    self.send_str(self.ok_str)


if __name__ == '__main__':
    serv = ThreadingTCPServer(('0.0.0.0', 16111), EchoHandler)
    print("Listening...")
    serv.serve_forever()
