import json
import logging
import shlex

from file_interface import FileInterface

class FileProtocol:
    def __init__(self):
        self.file = FileInterface()

    def proses_string(self, string_datamasuk=''):
        logging.warning(f"[PROTOCOL] Menerima string: {string_datamasuk}")
        try:
            c = shlex.split(string_datamasuk)
            if len(c) == 0:
                raise ValueError("Request kosong")

            c_request = c[0].strip().lower() 
            params = c[1:] 

            if hasattr(self.file, c_request):
                method = getattr(self.file, c_request)
                hasil = method(params)
            else:
                hasil = dict(status='ERROR', data='request tidak dikenali')
        except Exception as e:
            logging.error(f"[PROTOCOL] ERROR: {str(e)}")
            hasil = dict(status='ERROR', data='request tidak dikenali')
        return json.dumps(hasil) + '\r\n\r\n'

if __name__ == '__main__':
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET contoh.txt"))
    print(fp.proses_string("DELETE contoh.txt")) 
    print(fp.proses_string("UPLOAD test.txt 'c2FtcGxlIHRleHQ='"))
