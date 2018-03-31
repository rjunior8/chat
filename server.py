import socket
import ssl

def main():
	host = "server ip address"
	port = 8000
	clients = []
	s = socket.socket()
	s.bind((host, port))
	s.listen(5)
	c, addr = s.accept()
	print("Connection from: {}".format(addr))

	stream = ssl.wrap_socket(c, keyfile="/etc/ssl/private/ssl-cert-snakeoil.key",
											  certfile="/etc/ssl/certs/ssl-cert-snakeoil.pem",
											  server_side=True, cert_reqs=ssl.CERT_NONE,
											  ssl_version=ssl.PROTOCOL_TLSv1,
											  ca_certs="/etc/ssl/certs/ca-certificates.crt",
											  do_handshake_on_connect=False,
											  suppress_ragged_eofs=True, ciphers=None)

	while True:
		data = stream.recv(1024).decode("utf-8")
		if not data:
			break
		print("From connected user: {}".format(data))
		data = data.upper()
		print("Sending: {}".format(data))
		stream.send(data.encode("utf-8"))
	stream.close()

if __name__ == "__main__":
	main()
