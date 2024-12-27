import http.server
import socketserver
import os
import socket
import json
import datetime
from multiprocessing import Process
from pymongo import MongoClient
from urllib.parse import parse_qs
from dotenv import load_dotenv

# Завантаження змінних з .env
load_dotenv()

# Налаштування HTTP-сервера
PORT = 3000
STATIC_DIR = "static"

# Підключення до MongoDB Atlas
MONGODB_URI = os.getenv("MONGODB_URI")

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/front-init/index.html"
        elif self.path == "/message":
            self.path = "/front-init/message.html"
        elif self.path.startswith("/static/"):
            self.path = self.path[1:]
        else:
            self.path = "/front-init/error.html"
        return super().do_GET()

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = post_data.decode('utf-8')
            send_to_socket(data)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Message received")

def send_to_socket(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("localhost", 5000))
    sock.sendall(data.encode('utf-8'))
    sock.close()

# Налаштування Socket-сервера
def socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 5000))
    sock.listen(1)
    print("Socket server is running on port 5000")
    while True:
        client_socket, addr = sock.accept()
        with client_socket:
            data = client_socket.recv(1024)
            if data:
                data_dict = parse_qs(data.decode('utf-8'))
                data_dict = {key: value[0] for key, value in data_dict.items()}
                data_dict["date"] = str(datetime.datetime.now())
                save_to_mongodb(data_dict)

def save_to_mongodb(data):
    client = MongoClient(MONGODB_URI)
    db = client["messages_db"]
    collection = db["messages"]
    collection.insert_one(data)
    print("Data saved to MongoDB Atlas:", data)

# Запуск серверів
if __name__ == "__main__":
    httpd = socketserver.TCPServer(("", PORT), MyHttpRequestHandler)
    print(f"HTTP server is running on port {PORT}")

    socket_process = Process(target=socket_server)
    socket_process.start()

    httpd.serve_forever()
