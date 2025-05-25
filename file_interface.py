import logging
import os
import base64
from glob import glob

class FileInterface:
    def __init__(self):
        """
        Inisialisasi direktori penyimpanan file.
        Membuat folder 'files' di direktori script jika belum ada.
        Menyimpan direktori kerja asli dan direktori file.
        """
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            self.files_dir = os.path.normpath(os.path.join(base_path, 'files'))
            os.makedirs(self.files_dir, mode=0o755, exist_ok=True)
            if not os.path.isdir(self.files_dir):
                raise RuntimeError(f"Gagal membuat atau mengakses direktori: {self.files_dir}")
            self.original_dir = os.getcwd()
            logging.info(f"Direktori penyimpanan file siap di: {self.files_dir}")
        except Exception as e:
            logging.error(f"Gagal inisialisasi direktori: {str(e)}")
            raise

    def _change_to_files_dir(self):
        """Pindah ke direktori penyimpanan file."""
        try:
            os.chdir(self.files_dir)
        except Exception as e:
            logging.error(f"Gagal pindah ke direktori files: {str(e)}")
            raise

    def _restore_original_dir(self):
        """Kembali ke direktori kerja awal."""
        try:
            os.chdir(self.original_dir)
        except Exception as e:
            logging.error(f"Gagal kembali ke direktori awal: {str(e)}")
            raise

    def upload(self, params):
        """
        Upload file dengan parameter [filename, base64_data].
        Mengembalikan dict status dan pesan.
        """
        try:
            self._change_to_files_dir()
            filename = params[0]
            base64_data = params[1]
            decoded_data = base64.b64decode(base64_data.encode())
            with open(filename, 'wb') as f:
                f.write(decoded_data)
            return {'status': 'OK', 'data': f"{filename} berhasil diupload"}
        except Exception as e:
            return {'status': 'ERROR', 'data': str(e)}
        finally:
            self._restore_original_dir()

    def delete(self, params):
        """
        Hapus file dengan parameter [filename].
        Mengembalikan dict status dan pesan.
        """
        try:
            self._change_to_files_dir()
            filename = params[0]
            os.remove(filename)
            return {'status': 'OK', 'data': f"{filename} berhasil dihapus"}
        except Exception as e:
            return {'status': 'ERROR', 'data': str(e)}
        finally:
            self._restore_original_dir()

    def list(self, params=None):
        """
        List semua file di direktori penyimpanan.
        Mengembalikan dict status dan list nama file.
        """
        try:
            self._change_to_files_dir()
            filelist = glob('*.*')
            return {'status': 'OK', 'data': filelist}
        except Exception as e:
            return {'status': 'ERROR', 'data': str(e)}
        finally:
            self._restore_original_dir()

    def get(self, params):
        """
        Ambil file dengan parameter [filename].
        Mengembalikan dict status, nama file, dan data file base64.
        """
        try:
            self._change_to_files_dir()
            filename = params[0]
            if filename == '':
                return None
            with open(filename, 'rb') as f:
                file_content = f.read()
            encoded_content = base64.b64encode(file_content).decode()
            return {'status': 'OK', 'data_namafile': filename, 'data_file': encoded_content}
        except Exception as e:
            return {'status': 'ERROR', 'data': str(e)}
        finally:
            self._restore_original_dir()


if __name__ == '__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))
