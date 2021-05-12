### Day1 :'21.5.12
- 실습코드 다운로드 (단톡방 공유)
- pycharm(파이참)설치
- 실습코드 가상환경 프로젝트 폴더로 이동
- 파이참내 하단 터미널에서 openCV 모듈 설치 <br>
  : pip install opencv-contrib-python

<pre>
<code>
img = cv2.imread('aaa.jpg', 1)
</code>
</pre>
imread로 사진을 불러오고, 1은 칼라, 0은 흑백으로 불러옴을 의미

<pre>
<code>
 cv2.imshow('aaa Window', img)
 cv2.waitKey(0)
 cv2.destroyAllWindows()
</code>
</pre>
imshow는 사진을 창을 띄워서 보여 준다는 의미이고,인수 왼쪽은 창의 이름을, 오른쪽은 사진 변수이름을 적는다.
waitkey는 창을 띄우고 기다리는지 그냥 가는지 판단하는 것을 말하는데, 0을 넣으면 창을 띄운 상태로 멈춘다는 의미가
되고 1을 넣으면 창을 띄우고 바로 다음 코드를 실행하게 된다. 그 다음 코드가 destroyAllWondows, 즉 창을 닫는 것이므로
사진창이 띄워졌다가 바로 닫히게 된다. 실행이 매우 빠르기 때문에 창이 안 열린 것과 같이 느끼게 된다.

<code>
cv2.imwrite('aaa.jpg', img)
</code> <br><br>
imwrite로 사진을 저장

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

VideoCapture로 동영상 불러오는데, 현 폴더 안의 동영상을 보려면
동영상 이름을 적고, PC웹캠 실시간 동영상을 보려면 숫자 0을 넣는다
숫자 0은 현재 컴퓨터에 내장된 기본 카메라를 의미하고 또다른 카메라가
있으면 1을 넣게 된다.<br><br>

VideoCapture는 카메라를 찾는 것이고 capure.isOpened는 가동이
되는지 확인을 하는 것이다. while문은 무한루프 반복문으로 카메라가
이미지를 계속적으로 캡쳐를 반복하는 것은 영상을 불러온다는 의미가 된다.
카메라가 가동되면 캡쳐된 이미지를 read()로 읽어내는데 이 함수는 2가지
데이터를 이미지로부터 읽어낸다. 하나는 캡쳐된 이미지가 있는지 없는지
판단하는 true와 false 데이터, 다른 하나는 캡쳐된 이미지 화면을 배열로
변환하여 나타낸 데이터이다. 전자는 ret변수에 넣고, 후자는 frame변수에
들어가 저장되게 된다. 당연히 if문으로 ret에 데이터가 들어왔는지 확인해야
하고 없으면 break로 멈추게 된다. 
