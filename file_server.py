import socket
import threading
import logging
from file_protocol import FileProtocol

fp = FileProtocol()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address

    def run(self):
        buffer = b''
        while True:
            data = self.connection.recv(4096)
            if not data:
                break
            buffer += data
            while b"\r\n\r\n" in buffer:
                request_bytes, buffer = buffer.split(b"\r\n\r\n", 1)
                request_str = request_bytes.decode().strip()
                logging.warning(f"Request diterima: {request_str} dari {self.address}")
                hasil = fp.proses_string(request_str)
                hasil += "\r\n\r\n"
                self.connection.sendall(hasil.encode())
        self.connection.close()
        logging.warning(f"Connection closed: {self.address}")

class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=6666):
        threading.Thread.__init__(self)
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        logging.warning(f"Server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        while True:
            connection, client_address = self.my_socket.accept()
            logging.warning(f"Connection from {client_address}")
            clt = ProcessTheClient(connection, client_address)
            clt.start()
            self.the_clients.append(clt)

def main():
    logging.basicConfig(level=logging.WARNING)
    svr = Server(ipaddress='0.0.0.0', port=6666)
    svr.start()

if __name__ == "__main__":
    main()
