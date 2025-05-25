import os
import time
import csv
import subprocess
from itertools import product
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from file_client import FileClient

def generate_test_file(nama_file, ukuran_mb):
    chunk_size = 1024 * 1024  # 1MB
    ukuran = ukuran_mb * chunk_size
    if os.path.exists(nama_file):
        if os.path.getsize(nama_file) == ukuran:
            return nama_file
    with open(nama_file, 'wb') as f:
        for _ in range(ukuran_mb):
            f.write(os.urandom(chunk_size))
    return nama_file

def worker_upload(client, ukuran_file_mb, id_worker):
    nama_file = f"testfile_{ukuran_file_mb}mb.dat"
    file_sumber = f"source_{ukuran_file_mb}mb.dat"
    generate_test_file(file_sumber, ukuran_file_mb)
    with open(file_sumber, 'rb') as f:
        data_file = f.read()
    waktu_mulai = time.time()
    hasil = client.remote_upload(nama_file, data_file)
    waktu_berjalan = time.time() - waktu_mulai
    return {
        'sukses': hasil is not None and hasil.get('status') == 'OK',
        'waktu': waktu_berjalan,
        'byte': len(data_file),
        'id_worker': id_worker
    }

def worker_download(client, ukuran_file_mb, id_worker):
    nama_file = f"testfile_{ukuran_file_mb}mb.dat"
    waktu_mulai = time.time()
    hasil = client.remote_get(nama_file)
    waktu_berjalan = time.time() - waktu_mulai
    return {
        'sukses': hasil is not None,
        'waktu': waktu_berjalan,
        'byte': len(hasil) if hasil else 0,
        'id_worker': id_worker
    }

def jalankan_test(alamat_server, operasi, ukuran_file_mb, jumlah_worker, gunakan_pool_proses=False, tipe_server='thread'):
    kelas_executor = ThreadPoolExecutor if tipe_server == 'thread' else ProcessPoolExecutor
    fungsi_worker = worker_upload if operasi == 'upload' else worker_download
    client = FileClient(alamat_server)
    with kelas_executor(max_workers=jumlah_worker) as executor:
        futures = [executor.submit(fungsi_worker, client, ukuran_file_mb, i) for i in range(jumlah_worker)]
        hasil_list = [future.result() for future in as_completed(futures)]
    sukses_client = 1 if all(r['sukses'] for r in hasil_list) else 0
    gagal_client = 0 if sukses_client else 1
    total_byte = sum(r['byte'] for r in hasil_list if r['sukses'])
    waktu_maks = max(r['waktu'] for r in hasil_list) if hasil_list else 0
    throughput = total_byte / waktu_maks if waktu_maks > 0 else 0
    return {
        'operasi': operasi,
        'ukuran_file_mb': ukuran_file_mb,
        'jumlah_worker_client': jumlah_worker,
        'sukses': sukses_client,
        'gagal': gagal_client,
        'waktu_total': waktu_maks,
        'throughput': throughput,
        'total_byte': total_byte
    }

def mulai_server(tipe_server, jumlah_worker_server):
    if tipe_server == 'thread':
        cmd = ['python3', 'file_server_Multithreading.py', str(jumlah_worker_server)]
    else:
        cmd = ['python3', 'file_server_Multiprocessing.py', str(jumlah_worker_server)]
    return subprocess.Popen(cmd)

def jalankan_client_test(operasi, alamat_server, ukuran_file, jumlah_worker_client, gunakan_pool_proses, tipe_server):
    return jalankan_test(alamat_server, operasi, ukuran_file, jumlah_worker_client, gunakan_pool_proses, tipe_server)

def main():
    matriks_test = [
        ('upload', 10, 1),
        ('download', 10, 1),
        ('upload', 10, 5),
        ('download', 10, 5),
        ('upload', 10, 50),
        ('download', 10, 50),
        ('upload', 50, 1),
        ('download', 50, 1),
        ('upload', 50, 5),
        ('download', 50, 5),
        ('upload', 50, 50),
        ('download', 50, 50),
        ('upload', 100, 1),
        ('download', 100, 1),
        ('upload', 100, 5),
        ('download', 100, 5),
        ('upload', 100, 50),
        ('download', 100, 50)
    ]
    tipe_server_list = ['thread', 'process']
    jumlah_worker_server_list = [1, 5, 50]

    with open('hasil_stress_test.csv', 'w', newline='') as csvfile:
        kolom = [
            'id_test', 'operasi', 'ukuran_file_mb', 'jumlah_worker_client',
            'tipe_server', 'jumlah_worker_server', 'waktu_total',
            'throughput_bytes_per_detik', 'client_sukses', 'client_gagal'
        ]
        penulis = csv.DictWriter(csvfile, fieldnames=kolom)
        penulis.writeheader()
        id_test = 1
        for operasi, ukuran_file, jumlah_worker_client in matriks_test:
            for tipe_server, jumlah_worker_server in product(tipe_server_list, jumlah_worker_server_list):
                print(f"\nTest {id_test}: {operasi} {ukuran_file}MB dengan {jumlah_worker_client} client pada server {tipe_server} ({jumlah_worker_server} workers)")
                subprocess.run(['pkill', '-f', 'file_server'], stderr=subprocess.DEVNULL)
                time.sleep(1)
                proses_server = mulai_server(tipe_server, jumlah_worker_server)
                time.sleep(2)  # waktu untuk server siap
                try:
                    hasil = jalankan_client_test(operasi, 'localhost:6666', ukuran_file, jumlah_worker_client, False, tipe_server)
                    if not hasil:
                        penulis.writerow({
                            'id_test': id_test, 'operasi': operasi,
                            'ukuran_file_mb': ukuran_file, 'jumlah_worker_client': jumlah_worker_client,
                            'tipe_server': tipe_server, 'jumlah_worker_server': jumlah_worker_server
                        })
                        csvfile.flush()
                        id_test += 1
                        continue
                    penulis.writerow({
                        'id_test': id_test, 'operasi': operasi,
                        'ukuran_file_mb': ukuran_file, 'jumlah_worker_client': jumlah_worker_client,
                        'tipe_server': tipe_server, 'jumlah_worker_server': jumlah_worker_server,
                        'waktu_total': hasil['waktu_total'],
                        'throughput_bytes_per_detik': hasil['throughput'],
                        'client_sukses': hasil['sukses'],
                        'client_gagal': hasil['gagal']
                    })
                    csvfile.flush()
                    id_test += 1
                finally:
                    proses_server.terminate()
                    proses_server.wait()
                    time.sleep(1)

if __name__ == '__main__':
    main()
