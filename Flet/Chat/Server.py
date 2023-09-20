import socket
import threading
import flet as ft
import os
from ChatApp import Message, ChatMessage
from flask import Flask
from flask_cors import CORS

# localhost=127.0.0.1 et port 3000; test sur wifi IPV4= 192.168.0.--- port 3000
HOST = "192.168.0.---"
PORT = 3000
LISTENER_LIMIT = 5
CONNETION = []
THREAD = []
HEADER = "HTTP/1.1 201 CREATED\r\nContent-Length: 5\r\nHost: localhost:3000\r\nAccess-Control-Allow-Origin: *\r\nContent-Type: text/html; charset=utf-8\r\nBody: Hello\r\n\r\n"
DEFAULT_FLET_PATH = 'http:/localhost'
DEFAULT_FLET_PORT = 3000
app = Flask(__name__)
CORS(app)

@app.route("/")
def main(page: ft.Page):
  server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  page.title = "Chat Window"
  page.add(ft.Text("Connected Successfully"))
  
  try:
    server.bind((HOST, PORT))
    print(f"Running the server on {HOST}{PORT}")
  except:
    print(f"Unable to bind to host {HOST} and port {PORT}")
  
  server.listen(LISTENER_LIMIT)
  
  while 1:
    client, address = server.accept()
    with client:
      print(client)
      print(address)
      CONNETION.append([client, address])
      client.send(HEADER.encode())
      print(f"connected to client{address[0]} {address[1]}")
  
  p = 0
  while p < len(THREAD):
    THREAD[p].join()
    p += 1

def handleclient(client):
  while True:
    ct = client.recvfrom(1024)
    for i in CONNETION:
      if i[0] is not client:
        i[0].send(ct[0])

if __name__=="__main__":
    flet_path = os.getenv("FLET_PATH", DEFAULT_FLET_PATH)
    flet_port = int(os.getenv("FLET_PORT", DEFAULT_FLET_PORT))
    ft.app(target = main, view = ft.WEB_BROWSER)
    app.run(host = '192.168.0.---', port = 3000)
