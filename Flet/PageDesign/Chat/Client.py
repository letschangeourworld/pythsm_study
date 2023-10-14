import socket
import threading
import flet as ft
import os
from ChatApp import Message, ChatMessage
from flask import Flask
from flask_cors import CORS

# localhost=127.0.0.1 et port 3000; IPV4= 192.168.0.--- port 5000
HOST = "192.168.0.---"
PORT = 3000
DEFAULT_FLET_PATH = 'http:/localhost'  # or 'ui/path'
DEFAULT_FLET_PORT = 3000
app = Flask(__name__)
CORS(app)

@app.route("/")
def main(page: ft.Page):
    print("main")
    # 클라이언트 소켓 생성
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    page.title = "Chat Window"
    page.add(ft.Text("Connection"))
    
    # Host 연결
    try:
        client.connect((HOST, PORT))
        print(f"Connected to Host Server Successfully")
        n_client = client.recv(1024)
        print(n_client.decode())
        while n_client:
            message = input("Input Message")
            client.send(message.encode())
            n_client = client.recv(1024)
            print(n_client.decode())
    except:
        print(f"Unable to connect to server {HOST}{PORT}")

if __name__=="__main__":
    flet_path = os.getenv("FLET_PATH", DEFAULT_FLET_PATH)
    flet_port = int(os.getenv("FLET_PORT", DEFAULT_FLET_PORT))
    ft.app(target = main, view = ft.WEB_BROWSER)
    app.run(host = '192.168.0.---', port = 3000)
