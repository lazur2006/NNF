import qrcode
import socket

class QR(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
        # Link for website
        input_data = f"http://{self.get_ip()}:8888"
        #Creating an instance of qrcode
        qr = qrcode.QRCode(
                version=1,
                box_size=10,
                border=0)
        qr.add_data(input_data)
        qr.make(fit=True)
        #img = qr.make_image(fill='black', back_color='white')
        #img.save('static/images/qrcode.png')

    

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
