# QR코드 CSV 파일로 저장

from pyzbar.pyzbar import decode
from pyzbar import pyzbar
import cv2
import glob
import pandas as pd

def main():
    camera = cv2.VideoCapture(0)
    ret,frame = camera.read()
    lst = []
    df = pd.DataFrame(columns = ['qr'])
    while ret:
        ret,frame = camera.read()
        qrcodes = decode(frame)
        for qrcode in qrcodes:
            x, y, w, h = qrcode.rect
            qr_text = qrcode.data.decode('utf-8')
            print(qr_text)
            lst.append(qr_text)
            cv2.rectangle(frame,(x, y),(x+w, y+h),(0, 255, 0),2)
        cv2.imshow('QR code reader', frame)        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    camera.release()
    cv2.destroyAllWindows()
    df = pd.DataFrame(columns = ['QR'])
    df['QR'] = lst
    df.to_csv('qr_df1.csv')

if __name__ == '__main__':
    main()


# QR코드 text 파일로 저장
from pyzbar.pyzbar import decode
from pyzbar import pyzbar
import cv2

def main():
    camera = cv2.VideoCapture(0)
    ret,frame = camera.read()
    lst = []
    while ret:
        ret,frame = camera.read()
        qrcodes = decode(frame)
        for qrcode in qrcodes:
            x, y, w, h = qrcode.rect
            qr_text = qrcode.data.decode('utf-8')
            print(qr_text)
            lst.append(qr_text)
            cv2.rectangle(frame,(x, y),(x+w, y+h),(0, 255, 0),2)
        cv2.imshow('QR code reader', frame)        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    camera.release()
    cv2.destroyAllWindows()
    txt = lst[0]
    file = open('qrtx.txt', 'w')
    file.write(txt)
    file.close
    
if __name__ == '__main__':
    main()

