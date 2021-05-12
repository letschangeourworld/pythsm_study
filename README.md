1. Day1 :'21.5.12
* 실습코드 다운로드 (단톡방 공유)
* IDLE(통합개발환경) pycharm(파이참)설치
* 실습코드 가상환경 프로젝트 폴더로 이동
* 파이참내 하단 터미널에서 openCV 모듈 설치
  pip install opencv-contrib-python
* cv2 모듈내 함수기능

<pre>
<code>
img = cv2.imread('aaa.jpg', 1)
</code>
</pre>
사진을 불러 오는데, 1은 칼라, 0은 흑백을 의미함

<pre>
<code>
 cv2.imshow('aaa Window', img)
 cv2.waitKey(0)
 cv2.destroyAllWindows()
</code>
</pre>
imshow는 사진을 창을 띄워서 보여 준다는 의미이고,
인수 왼쪽은 창의 이름을, 오른쪽은 사진 변수이름을 적는다.
waitkey는 창을 띄우고 기다리는지 그냥 가는지 판단하는
것을 말하는데, 0을 넣으면 창을 띄운 상태로 멈춘다는 의미가
되고 1을 넣으면 창을 띄우고 바로 다음 코드를 실행하게 된다.
그 다음 코드가 destroyAllWondows, 즉 창을 닫는 것이므로
사진창이 띄워졌다가 바로 닫히게 된다. 실행이 매우 빠르기
때문에 창이 안 열린 것과 같이 느끼게 된다.

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
