import os
import sys
import cmd
import ssl
import time
import socket
import signal
import traceback
from threading import Thread
from termcolor import colored, cprint

debug = True

class colors:
    default = '\033[0;0m'
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'


class TcpClient(cmd.Cmd):

  intro = colored("Welcome to pt pHASE console","yellow") + colored(" to get help press ", "red") + colored("!help", "blue")

  host = "localhost"
  port = 8000
  user = "user01"
  password = "123456"
  sock = None
  ssl_sock = None
  rt = None
  connected = False
  #commands = []


  def __init__(self, user, password):
    super(TcpClient, self).__init__()
    self.user=user
    self.prompt = colors.purple + user + colors.green +" > " + colors.default + " "   #TODO: use colored() here
    try:
      self.connect()
    except:
      cprint("Can not connect to TCP Server", "white", "on_red")
      if debug: traceback.print_exc(file=sys.stdout)


#-------------------------------------------------------------------------------
#CMD STUFF
#-------------------------------------------------------------------------------
  def do_exit(self, s):
    os.killpg(os.getpid(), signal.SIGTERM)
    return True


  def default(self, line):
    print("processing... maybe asynchronus (that means the answer comes later)")
    if line[0] == "!":
      line = line[1:]
    self.send(line)
    #commands.append(line)


#-------------------------------------------------------------------------------
#SOCKET STUFF
#-------------------------------------------------------------------------------
  def connect(self):
    if not self.rt == None:
      try:
        self.rt.join()
      except:
        print("receier thread already gone")
        if debug: traceback.print_exc(file=sys.stdout)

    while not self.connected:
      try:     
        self.sock = socket.socket()

        self.ssl_sock = ssl.wrap_socket(self.sock,
                                        keyfile="server.key",
                                        certfile="server.crt",
                                        server_side=False, cert_reqs=ssl.CERT_NONE,
                                        ssl_version=ssl.PROTOCOL_TLSv1_2,
                                        ca_certs=ssl.CERT_NONE,
                                        do_handshake_on_connect=False,
                                        suppress_ragged_eofs=True, ciphers=None)

        self.ssl_sock.connect((self.host, self.port))
        rt = Thread(target=self.receiverThread, args = (self.ssl_sock,))
        rt.start()
        self.connected=True
        print("connected")
      except:
        if debug: traceback.print_exc(file=sys.stdout)
        print("...trying to reconnect")
        time.sleep(5)



  #the thread that does all the receiving from the server
  def receiverThread(self, ssl_sock):
    while True:                                                                 #loops eternally and because next row...
      data = ssl_sock.recv(1024).decode("utf-8")                                #...blocks until a packet is received it will not consume all CPU ressources
      if not data:                                                              #if no data is received (=server disconnected)
        print("CONNECTION ENDED")                                               #means that the program can end
        self.ssl_sock.close()                       #TODO sslsock too?
        self.connected = False
        self.connect()
        break
      print(data)

  #this thread does all the sending to the server
  def send(self, line):
    try:
      self.ssl_sock.send(bytes("[{}]: {}".format(socket.gethostname(), line + "\n").encode("utf-8")))
      if debug: print("package sent")
    except:
      print("lost connection, trying to reconnect")
      if debug: traceback.print_exc(file=sys.stdout)
      self.ssl_sock.close()                      #TODO normal socket too?
      self.connected = False
      self.connect()


      
def main ():
  if len(sys.argv) < 2:
    cprint("please specify username as first parameter:")
    cprint(" => python3 client.py LANDeV", "white", "on_red")
  else:
    print(sys.argv[1])
    c = TcpClient(sys.argv[1], "123456")
    c.cmdloop()


if __name__ == "__main__":
  main()
  
  
