1. Day1 :'21.5.12
* 실습코드 다운로드 (단톡방 공유)
* IDLE(통합개발환경) pycharm(파이참)설치
* 실습코드 가상환경 프로젝트 폴더로 이동
* 파이참내 하단 터미널에서 openCV 모듈 설치
  pip install opencv-contrib-python
* cv2 모듈내 함수기능

<code>
img = cv2.imread('aaa.jpg', 1)
</code><br>
사진을 불러오는데 1은 칼라로, 0은 흑백으로 불러오기

<pre>
<code>
 cv2.imshow('aaa Window', img)
 cv2.waitKey(0)
 cv2.destroyAllWindows()
</code>
</pre>
불러온 사진을 창을 띄워서 보여주고 창이름은 'aaa Window'로 한다. 

<code>
cv2.imwrite('aaa.jpg', img)
</code>

<pre>
<code>
capture = cv2.VideoCapture('video.mp4')

while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break
    cv2.imshow('Video Window’, frame)
    cv2.waitKey(25)
capture.release()
cv2.destroyAllWindows()
</code>
</pre>
