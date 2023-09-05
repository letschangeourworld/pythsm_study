
import cv2

# PC webcam 으로 영상보기
cap = cv2.VideoCapture(0)

frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
framCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_size = (frameWidth, frameHeight)
print('frame_size = ', frame_size)

fps = int(cap.get(cv2.CAP_PROP_FPS))
print('FPS = ', fps)

while True:
  ret, img = cap.read()
  if not(ret):
    break
  
  cv2.imshow('img', img)
  # cv2.resizeWindow(winname = 'img',width=200, height=150)    
  # q 키를 누르면 화면해제 (특정키 조작)
  # if cv2.waitKey(1) & 0xff == ord('q'):
  #     break
  
  # esc 키를 누르면 화면해제
  if cv2.waitKey(1) == 27:
    break

cap.release()
cv2.destroyAllWindows()
