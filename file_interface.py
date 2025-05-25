import os
import json
import base64
from glob import glob

class FileInterface:
    def __init__(self):
        if not os.path.exists('files/'):
            os.makedirs('files/')
        os.chdir('files/')

    def list(self, params=[]):
        try:
            filelist = glob('*.*')
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            if filename == '':
                return dict(status='ERROR', data='Nama file kosong')
            with open(filename, 'rb') as fp:
                isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            filename = params[0]
            filecontent = params[1]
            missing_padding = len(filecontent) % 4
            if missing_padding != 0:
                filecontent += '=' * (4 - missing_padding)
            filecontent = base64.b64decode(filecontent)
            with open(filename, 'wb') as fp:
                fp.write(filecontent)
            return dict(status='OK', data=f"{filename} uploaded successfully")
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = params[0]
            os.remove(filename)
            return dict(status='OK', data=f"{filename} deleted successfully")
        except Exception as e:
            return dict(status='ERROR', data=str(e))


if __name__ == '__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['example.jpg']))
    print(f.upload(['example_upload.jpg', base64.b64encode(b'This is a test file content').decode('utf-8')]))
    print(f.delete(['example_upload.jpg']))
