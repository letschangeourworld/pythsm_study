

if __name__ == "__main__":
    # find the webcam
    capture = cv2.VideoCapture(0)

    # video recorder
    fourcc = cv2.cv.CV_FOURCC(*'XVID')  # cv2.VideoWriter_fourcc() does not exist
    video_writer = cv2.VideoWriter("output.avi", fourcc, 20, (680, 480))

    # record video
    while (capture.isOpened()):
        ret, frame = capture.read()
        if ret:
            video_writer.write(frame)
            cv2.imshow('Video Stream', frame)

        else:
            break

    capture.release()
    video_writer.release()
    cv2.destroyAllWindows()
    
###############################################
    
import cv2
import time

cap = cv2.VideoCapture(0)

width = int(cap.get(3))
height = int(cap.get(4))
fcc = cv2.VideoWriter_fourcc(*'XVID')
#writer = cv2.VideoWriter('e:/test.avi', fcc, 60.0, (width, height))
recording = False
videono = 0

while(1):
    ret, frame = cap.read()
    hms = time.strftime('%H:%M:%S', time.localtime())

    cv2.putText(frame, str(hms), (0, 15), cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255))

    cv2.imshow('frame', frame)

    k = cv2.waitKey(1) & 0xff
    if k == ord('r') and recording is False:
        path = 'e:/test_' + str(videono) + '.avi'
        videono += 1
        print(path+' recording')
        writer = cv2.VideoWriter(path, fcc, 30.0, (width, height))
        recording = True

    if recording:
        writer.write(frame)

    if k == ord('e'):
        print('recording finished')
        recording = False
        writer.release()

cap.release()
cv2.destroyAllWindows()
    