import ssl
import socket
from threading import Thread

class TcpClient:
  def init():
    host = "localhost"
    port = 8000

    s = socket.socket()

    ssl_sock = ssl.wrap_socket(s, keyfile="server.key",
                                  certfile="server.crt",
                                  server_side=False, cert_reqs=ssl.CERT_NONE,
                                  ssl_version=ssl.PROTOCOL_TLSv1,
                                  ca_certs=ssl.CERT_NONE,
                                  do_handshake_on_connect=False,
                                  suppress_ragged_eofs=True, ciphers=None)

    ssl_sock.connect((host, port))
    rt = Thread(target=TcpClient.receiverThread, args = (ssl_sock,))
    rt.start()
    st = Thread(target=TcpClient.senderThread, args = (ssl_sock,))
    st.start()


  def receiverThread(ssl_sock):
    while True:
      data = ssl_sock.recv(1024).decode("utf-8")
      if not data:
        print("CONNECTION ENDED")
        break
      print(data)


  def senderThread(ssl_sock):
    message = input("<{}> ".format(socket.gethostname()))
    while message != "exit()":
      ssl_sock.send(bytes("[{}]: {}".format(socket.gethostname(), message).encode("utf-8")))
      message = input("<{}> ".format(socket.gethostname()))
    ssl_sock.close()

if __name__ == "__main__":
  TcpClient.init()
