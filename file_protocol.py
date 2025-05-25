import json
import logging
import shlex

from file_interface import FileInterface

class FileProtocol:
    def __init__(self):
        self.file_interface = FileInterface()

    def proses_string(self, input_string=''):
        """
        Memproses string perintah yang diterima dari client,
        menerjemahkan perintah sesuai protokol, dan mengembalikan
        hasil dalam format JSON string.
        """
        try:
            if '\r\n' in input_string:
                header, body = input_string.split('\r\n', 1)
            else:
                header, body = input_string, ''

            # Parsing command dan parameter menggunakan shlex agar aman
            tokens = shlex.split(header.lower())
            command = tokens[0].strip()
            params = tokens[1:]

            logging.warning(f"Memproses request: {command}")

            if command == 'upload':
                response = getattr(self.file_interface, command)([params[0], body.strip()])
            else:
                response = getattr(self.file_interface, command)(params)

            return json.dumps(response)

        except Exception as e:
            logging.error(f"Error memproses request: {str(e)}")
            return json.dumps({'status': 'ERROR', 'data': 'request tidak dikenali'})

if __name__ == '__main__':
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET pokijan.jpg"))
