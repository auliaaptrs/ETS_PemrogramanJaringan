import socket
import logging
import sys
from multiprocessing import Pool
from file_protocol import FileProtocol

class ClientProcessHandler:
    def __init__(self):
        self.file_protocol = FileProtocol()

    def __call__(self, conn_addr):
        connection, address = conn_addr
        data_buffer = ''
        try:
            while True:
                data = connection.recv(8192)
                if not data:
                    break
                data_buffer += data.decode()
                if "\r\n\r\n" in data_buffer:
                    response = self.file_protocol.proses_string(data_buffer.strip())
                    response += "\r\n\r\n"
                    connection.sendall(response.encode())
                    break
        except Exception as e:
            logging.error(f"Error saat memproses client {address}: {e}")
        finally:
            connection.close()
        return True

class ProcessPoolServer:
    def __init__(self, ip='0.0.0.0', port=6666, max_workers=5):
        self.address = (ip, port)
        self.max_workers = max_workers
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.pool = Pool(processes=self.max_workers)

    def run(self):
        logging.warning(f"Server berjalan di {self.address} dengan process pool max_workers={self.max_workers}")
        self.server_socket.bind(self.address)
        self.server_socket.listen(5)
        client_handler = ClientProcessHandler()
        try:
            while True:
                connection, client_addr = self.server_socket.accept()
                logging.warning(f"Connection dari {client_addr}")
                self.pool.apply_async(client_handler, args=((connection, client_addr),))
        except KeyboardInterrupt:
            logging.warning("Server dihentikan oleh user")
        finally:
            self.pool.close()
            self.pool.join()
            self.server_socket.close()

def main():
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    max_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    server = ProcessPoolServer(ip='0.0.0.0', port=6666, max_workers=max_workers)
    server.run()

if __name__ == "__main__":
    main()
