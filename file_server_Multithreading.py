import socket
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from file_protocol import FileProtocol

class ClientThreadHandler:
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        self.fp = FileProtocol()

    def run(self):
        data_buffer = ''
        try:
            while True:
                data = self.connection.recv(8192)
                if not data:
                    break
                data_buffer += data.decode()
                if "\r\n\r\n" in data_buffer:
                    response = self.fp.proses_string(data_buffer.strip())
                    response += "\r\n\r\n"
                    self.connection.sendall(response.encode())
                    break
        except Exception as e:
            logging.error(f"Error saat memproses client {self.address}: {e}")
        finally:
            self.connection.close()
        return True

class ThreadPoolServer:
    def __init__(self, ipaddress='0.0.0.0', port=6666, max_workers=5):
        self.ipinfo = (ipaddress, port)
        self.max_workers = max_workers
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)

    def run(self):
        logging.warning(f"Server berjalan di {self.ipinfo} dengan thread pool max_workers={self.max_workers}")
        self.server_socket.bind(self.ipinfo)
        self.server_socket.listen(5)
        try:
            while True:
                connection, client_address = self.server_socket.accept()
                logging.warning(f"Connection dari {client_address}")
                client_handler = ClientThreadHandler(connection, client_address)
                self.thread_pool.submit(client_handler.run)
        except KeyboardInterrupt:
            logging.warning("Server dihentikan oleh user")
        finally:
            self.thread_pool.shutdown(wait=True)
            self.server_socket.close()

def main():
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    max_workers = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    server = ThreadPoolServer(ipaddress='0.0.0.0', port=6666, max_workers=max_workers)
    server.run()

if __name__ == "__main__":
    main()
