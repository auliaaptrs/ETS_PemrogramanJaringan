import socket
import json
import base64
import logging

server_address = ('localhost', 6666) 
def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        logging.warning("sending message")
        sock.sendall((command_str + "\r\n\r\n").encode())
        
        data_received = ""
        while True:
            data = sock.recv(4096) 
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        
        data_received = data_received.replace("\r\n\r\n", "")
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        return False
    finally:
        sock.close()

def remote_list():
    command_str = "LIST"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print("Daftar file:")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal mengambil daftar file.")
        return False

def remote_get(filename=""):
    command_str = f"GET {filename}"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        namafile = hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        with open(namafile, 'wb') as fp:
            fp.write(isifile)
        print(f"File {namafile} berhasil disimpan.")
        return True
    else:
        print("Gagal mengambil file.")
        return False

def remote_upload(local_filepath=""):
    try:
        with open(local_filepath, 'rb') as f:
            filedata = f.read()
        filedata_b64 = base64.b64encode(filedata).decode('utf-8')
        filename = local_filepath.split('/')[-1] 
        command_str = f"UPLOAD {filename} {filedata_b64}"
        hasil = send_command(command_str)
        if hasil and hasil['status'] == 'OK':
            print(f"File {filename} berhasil diupload.")
            return True
        else:
            print("Gagal mengupload file:", hasil.get('data', ''))
            return False
    except FileNotFoundError:
        print("File lokal tidak ditemukan.")
        return False
    except Exception as e:
        print("Error saat upload:", e)
        return False

def remote_delete(filename=""):
    if not filename:
        print("Nama file harus diisi untuk DELETE.")
        return False
    command_str = f"DELETE {filename}"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print(f"File {filename} berhasil dihapus.")
        return True
    else:
        print("Gagal menghapus file:", hasil.get('data', ''))
        return False


if __name__ == '__main__':
    while True:
        cmd = input("Masukkan perintah (LIST, GET <nama_file>, UPLOAD <path_file>, DELETE <nama_file>, QUIT): ").strip()
        if cmd.upper() == 'QUIT':
            print("Keluar dari client.")
            break
        elif cmd.upper() == 'LIST':
            remote_list()
        elif cmd.upper().startswith('GET '):
            filename = cmd[4:].strip()
            if filename:
                remote_get(filename)
            else:
                print("Nama file harus diisi untuk GET.")
        elif cmd.upper().startswith('UPLOAD '):
            local_path = cmd[7:].strip()
            if local_path:
                remote_upload(local_path)
            else:
                print("Path file lokal harus diisi untuk UPLOAD.")
        elif cmd.upper().startswith('DELETE '):
            filename = cmd[7:].strip()
            if filename:
                remote_delete(filename)
            else:
                print("Nama file harus diisi untuk DELETE.")
        else:
            print("Perintah tidak dikenali.")
