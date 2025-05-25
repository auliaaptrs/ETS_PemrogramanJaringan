import socket
import json
import base64

class FileClient:
    def __init__(self, server_address='localhost:6666'):
        if isinstance(server_address, str):
            host, port = server_address.split(':')
            self.server_address = (host, int(port))
        else:
            self.server_address = server_address

    def send_command(self, command_str=""):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(self.server_address)
            sock.sendall((command_str + "\r\n\r\n").encode())
            data_received = b""
            while True:
                data = sock.recv(8192)
                if data:
                    data_received += data
                    if b"\r\n\r\n" in data_received:
                        break
                else:
                    break
            hasil = json.loads(data_received.decode())
            return hasil
        except Exception as e:
            print(f"Error saat komunikasi dengan server: {e}")
            return None
        finally:
            sock.close()

    def remote_upload(self, filename, file_data):
        chunk_size = 10 * 1024 * 1024  # 10MB chunks
        encoded_chunks = []
        for i in range(0, len(file_data), chunk_size):
            chunk = file_data[i:i+chunk_size]
            encoded_chunks.append(base64.b64encode(chunk).decode())
        command_str = f"UPLOAD {filename}\r\n" + "".join(encoded_chunks) + "\r\n\r\n"
        return self.send_command(command_str)

    def remote_get(self, filename):
        command_str = f"GET {filename}\r\n\r\n"
        hasil = self.send_command(command_str)
        if hasil and hasil.get('status') == 'OK':
            return base64.b64decode(hasil['data_file'])
        return None
