import os
import sys
import ssl
import time
import socket
import signal
import traceback
from threading import Thread

debug = True

class TcpClient:

  host = "localhost"
  port = 8000
  sock = None
  rt = None
  connected = False

  def init():
    TcpClient.connect()



  def connect():
    if not TcpClient.rt == None:
      try:
        TcpClient.rt.join()
      except:
        print("receier thread already gone")

    while not TcpClient.connected:
      try:     
        TcpClient.sock = socket.socket()

        ssl_sock = ssl.wrap_socket(TcpClient.sock, keyfile="server.key",
                                      certfile="server.crt",
                                      server_side=False, cert_reqs=ssl.CERT_NONE,
                                      ssl_version=ssl.PROTOCOL_TLSv1_2,
                                      ca_certs=ssl.CERT_NONE,
                                      do_handshake_on_connect=False,
                                      suppress_ragged_eofs=True, ciphers=None)

        ssl_sock.connect((TcpClient.host, TcpClient.port))
        rt = Thread(target=TcpClient.receiverThread, args = (ssl_sock,))
        rt.start()
        st = Thread(target=TcpClient.senderThread, args = (ssl_sock,))
        st.start()
        TcpClient.connected=True
        print("connected")
      except:
        if debug: traceback.print_exc(file=sys.stdout)
        time.sleep(5)
        print("...trying to reconnect")


  #the thread that does all the receiving from the server
  def receiverThread(ssl_sock):
    while True:                                                                 #loops eternally and because next row...
      data = ssl_sock.recv(1024).decode("utf-8")                                #...blocks until a packet is received it will not consume all CPU ressources
      if not data:                                                              #if no data is received (=server disconnected)
        print("CONNECTION ENDED")                                               #means that the program can end
        TcpClient.sock.close()
        TcpClient.connected = False
        TcpClient.connect()
        break
      print(data)

  #this thread does all the sending to the server
  def senderThread(ssl_sock):
    print("senderThread()")
    try:
      message = input("<{}> ".format(socket.gethostname()))
      while message != "exit()":
        print("Sender while loop")
        ssl_sock.send(bytes("[{}]: {}".format(socket.gethostname(), message).encode("utf-8")))
        print("package sent")
        message = input("<{}> ".format(socket.gethostname()))
      ssl_sock.close()
      #os.killpg(os.getpid(), signal.SIGTERM)                                      #Killing the app because receiver Thread still runs
      #exit(0)
    except:
      print("lost connection, trying to reconnect")
      TcpClient.sock.close()
      TcpClient.connected = False
      TcpClient.connect()


if __name__ == "__main__":
  TcpClient.init()
