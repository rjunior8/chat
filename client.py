import socket
import ssl

def main():
	host = "server ip addr"
	port = 8000

	s = socket.socket()

	ssl_sock = ssl.wrap_socket(s, keyfile="/etc/ssl/private/ssl-cert-snakeoil.key",
											  certfile="/etc/ssl/certs/ssl-cert-snakeoil.pem",
											  server_side=False, cert_reqs=ssl.CERT_NONE,
											  ssl_version=ssl.PROTOCOL_TLSv1,
											  ca_certs="/etc/ssl/certs/ca-certificates.crt",
											  do_handshake_on_connect=False,
											  suppress_ragged_eofs=True, ciphers=None)

	ssl_sock.connect((host, port))

	message = input("<{}> ".format(socket.gethostname()))
	while message != "exit()":
		ssl_sock.send(bytes("[{}]: {}".format(socket.gethostname(), message).encode("utf-8")))
		data = ssl_sock.recv(1024).decode("utf-8")
		print(data)
		message = input("<{}> ".format(socket.gethostname()))
	ssl_sock.close()

if __name__ == "__main__":
	main()
