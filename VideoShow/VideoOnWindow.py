import cv2
import platform

src = 0
if platform.system() == 'Windows':
    cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
else:
    cap = cv2.VideoCapture(src)
    
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

while cap.isOpened():
    grabbed, frame = cap.read()
    
    if grabbed:
        cv2.imshow('Camera Window', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

cap.release()
cv2.destroyAllWindows()
