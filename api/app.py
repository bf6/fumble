import socket
import threading
import time
from http.server import HTTPServer

from handler import FumbleHandler
from db import MongoDB


MongoDB().recreate()


addr = ('0.0.0.0', 8000)
sock = socket.socket()
# One socket, many threads
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(addr)
sock.listen(5)


class Thread(threading.Thread):
    def __init__(self, i):
        super().__init__()
        self.i = i
        # ctrl-c will kill process
        self.daemon = True
        self.start()

    def run(self):
        server = HTTPServer(addr, FumbleHandler, False)
        server.socket = sock
        server.server_bind = self.server_close = lambda self: None
        server.serve_forever()

# Default connection pool size for MongoClient
[Thread(i) for i in range(100)]

while True:
    time.sleep(1)
