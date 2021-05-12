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
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpen():
	print('width: {}, height : {}'.format(cap.get(3), cap.get(4))

while True:
	ret, fram = cap.read()
	if ret:
		gray = cv2.cvtColor(fram, cv2.COLOR_BGR2GRAY)
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
cv2.VideoCapture()를 사용해 비디오 캡쳐 객체를 생성할 수 있다. 안의 숫자는 장치 인덱스(어떤 카메라를 사용할 것인가)이다. 
1개만 부착되어 있으면 0, 2개 이상이면 첫 웹캠은 0, 두번째 웹캠은 1으로 지정한다.
cap.isOpen() : 비디오 캡쳐 객체가 정상적으로 Open되었는지 확인한다.
while True: 특정 키를 누를때까지 무한 반복을 위해 사용했다.
ret, fram = cap.read() : 비디오의 한 프레임씩 읽는다. 제대로 프레임을 읽으면 ret값이 True, 실패하면 False가 나타난다. 
fram에 읽은 프레임이 나온다.
cv2.cvtColor() : frame을 흑백으로 변환한다.
cap.release() : 오픈한 캡쳐 객체를 해제한다.
<br>
