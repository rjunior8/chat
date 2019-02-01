
import ssl
import time
import socket
from socket import *
from threading import Thread

#TO GENERATE THE CERTIFICATES use following Linux commands:
#openssl genrsa -des3 -out server.orig.key 2048
#openssl rsa -in server.orig.key -out server.key
#openssl req -new -key server.key -out server.csr
#openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt

CONNECTION = 0; ADDRESS = 1; STREAM = 2

class TcpServer:

  clients = []
  threads = []

  def init():
    host = "localhost"
    port = 8000
    clients = []
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)                                   #TO circumvent the "PORT STILL IN USE" error
    s.bind((host, port))
    s.listen(5)
    cl = Thread(target=TcpServer.clientListener, args = (s,))                                #The Thread that listens for new incoming clients
    cl.start()

  def clientListener(s):
    while True:
      c, addr = s.accept()
      print("New Connection from: {}".format(addr))

      stream = ssl.wrap_socket(c, keyfile="server.key",
                                  certfile="server.crt",
                                  server_side=True, cert_reqs=ssl.CERT_NONE,
                                  ssl_version=ssl.PROTOCOL_TLSv1,
                                  ca_certs=ssl.CERT_NONE,
                                  do_handshake_on_connect=False,
                                  suppress_ragged_eofs=True, ciphers=None)

      TcpServer.clients.append([c, addr, stream])
      
      ct = Thread(target=TcpServer.clientHandler, args = (c, addr, stream))
      TcpServer.threads.append(ct)
      ct.start()

  #method that handles the clients transmissions
  def clientHandler(c, addr, stream):
    while True:
      data = stream.recv(1024).decode("utf-8")
      if not data:
        TcpServer.removeClient([c, addr, stream])
        break
      print("From connected user: {}".format(data))
      data = data.upper()
      print("Sending: {}".format(data))
      TcpServer.notifyAll(data)
    #stream.close()


  #remove the client from the array so that it will not be notified
  def removeClient(client):
    TcpServer.clients.remove(client)
    print("removed " + str(client[ADDRESS]) + " from clients")
    print("lasting Clients: "+ str(TcpServer.clients))


  #go through the connected clients and send it to each client
  def notifyAll(data):
    for client in TcpServer.clients:
      print("Sending to " + str(client[ADDRESS]))
      client[STREAM].send(data.encode("utf-8"))


if __name__ == "__main__":
  TcpServer.init()
  
