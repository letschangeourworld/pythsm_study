import cv2
import platform

# 외부접속
ip = "000.000.000.000"
port = 51216
user = "iii"
password = "aaa"
url = f'rtsp://{user}:{password}@{ip}:{port}/11'

# # PC Webcam 접속
# url = 0

if platform.system() == 'Windows':
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
else:
    cap = cv2.VideoCapture(url)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while cap.isOpened():
    grabbed, frame = cap.read()
    
    if grabbed:
        cv2.imshow('Camera Window', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()
