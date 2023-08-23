import numpy as np
import qrcode
from PIL import Image

qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=10,border=4)

qr.add_data('https://github.com/letschangeourworld/pythsm_study')
qr.make(fit=True)
print("The shape of the QR image:", np.array(qr.get_matrix()).shape)
img = qr.make_image(fill_color='black',back_color='white')
img.save('my_qrcode.png')


from pyzbar.pyzbar import decode
import cv2

img1 = Image.open('my_qrcode.png')
result = decode(img1)
for i in result:
    print(i.data.decode('utf-8'))


import cv2
from pyzbar import pyzbar

def read_qrcodes(frame):
    qrcodes = pyzbar.decode(frame)
    for qrcode in qrcodes:
        x, y , w, h = qrcode.rect
        qrcode_text = qrcode.data.decode('utf-8')
        print(qrcode_text)
        cv2.rectangle(frame,(x, y),(x+w, y+h),(0, 255, 0),2)
    return frame

def main():
    camera = cv2.VideoCapture(0)
    ret,frame = camera.read()
    while ret:
        ret,frame = camera.read()
        frame = read_qrcodes(frame)
        cv2.imshow('QR code reader', frame)
        if cv2.waitKey(0) & 0xFF == 27:
            break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
