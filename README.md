### Day1 :'21.5.12
- 실습코드 다운로드 (단톡방 공유)
- pycharm 설치 (구글검색하여 무료다운로드)
- 실습코드 가상환경 프로젝트 폴더로 이동
- 파이참 하단 터미널에서 openCV 모듈 설치 <br>
  pip install opencv-contrib-python

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
imshow는 사진을 창을 띄워서 보여 준다는 의미이고, 인수 왼쪽은 창의 이름을, 오른쪽은 사진 변수이름을 적는다.
waitkey는 창을 띄우고 기다리는지 그냥 가는지 판단하는 것을 말하는데, 0을 넣으면 창을 띄운 상태로 멈춘다는 의미가
되고 1을 넣으면 창을 띄우고 바로 다음 코드를 실행하게 된다. 그 다음 코드가 destroyAllWondows, 즉 창을 닫는 것이므로
사진창이 띄워졌다가 바로 닫히게 된다. 실행이 매우 빠르기 때문에 창이 안 열린 것과 같이 느끼게 된다.

<code>
cv2.imwrite('aaa.jpg', img)
</code> <br><br>
imwrite로 사진을 저장

<pre>
<code>
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpen():
	print('width: {}, height : {}'.format(cap.get(3), cap.get(4))

while True:
	ret, frame = cap.read()
	if ret:
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		cv2.imshow('video', gray)
		k == cv2.waitKey(1) & 0xFF
		if k == 27:
			break
	else:
		print('error')
cap.release()
cv2.destroyAllWindows()

</code>
</pre>
* cv2.VideoCapture() : 비디오 캡쳐 객체 생성 <br>
입력 숫자 : 장치 인덱스로 어떤 카메라를 사용할 것인가를 뜻함 <br> 
장치에 카메라 1개만 부착되어 있을 경우 : 0 (보통 기본 내장 카메라) <br>
장치에 카메라가 2개 이상 부탁되어 있을 경우 : 0 (첫번째 웹캠), 1 (두번째 웹캠) <br>

* cap.isOpen() : 비디오 캡쳐 객체가 정상적으로 Open되었는지 확인
* while True   : 특정 키를 누를 때까지 무한 반복
* ret, frame = cap.read() : 비디오의 한 프레임씩 읽음
  프레임은 영상의 한 컷을 의미 
  프레임을 제대로 읽으면 ret 변수에 True 입력됨 
  프레임을 읽지 못하면 ret 변수에 False 입력됨 
  프레임을 읽으면 읽은 프레임 스크린 데이터를 frame변수에 array값으로 입력됨
* cv2.cvtColor() : frame을 흑백으로 변환한다.
* cap.release()  : 오픈한 캡쳐 객체를 해제한다.
<br>
