1. Day1 :'21.5.12
* 실습코드 다운로드 (단톡방 공유)
* IDLE(통합개발환경) pycharm(파이참)설치
* 실습코드 가상환경 프로젝트 폴더로 이동
* 파이참내 하단 터미널에서 openCV 모듈 설치
  pip install opencv-contrib-python
* cv2 모듈내 함수기능

<code>
img = cv2.imread('aaa.jpg', 1) 
</code>

<code>
 cv2.imshow('aaa Window', img)
 cv2.waitKey(0)
 cv2.destroyAllWindows()
</code>


<code>
cv2.imwrite('daria_gray.jpg', img)
</code>

<code>
capture = cv2.VideoCapture('swan.mp4')

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break
    cv2.imshow('Video Window’, frame)
    cv2.waitKey(25)
 capture.release()
 cv2.destroyAllWindows()
</code>
