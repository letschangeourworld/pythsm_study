### Day1 :'21.5.12

* 실습코드 다운로드 (파이썬더 단톡방 공유) <br>
* pycharm 설치 (pycharm사이트에 가서 community용 무료 다운로드 설치) <br>
* 실습코드 파일을 가상환경 프로젝트 폴더로 이동 <br>
* 파이참(pycharm) 하단 터미널을 클릭 → 터미널 창에서 openCV 모듈 설치 <br>
     입력/실행 → <b>pip install opencv-contrib-python</b> <br>

<pre>
<code>
img = cv2.imread('aaa.jpg', 1)
</code>
</pre>

* <b>imread :</b> 사진 불러오기 <br>
     - 좌측 인수 : 사진파일 경로입력 <br>
     - 우측 인수 <br>
        - 1 : 칼라 <br>
        - 0 : 흑백 <br>

<pre>
<code>
 cv2.imshow('aaa Window', img)
 cv2.waitKey(0)
 cv2.destroyAllWindows()
</code>
</pre>

* <b>imshow :</b> 사진을 창을 띄워서 보여 줌 <br>
     - 인수 왼쪽 : 창 이름 <br>
     - 인수 오른쪽 : 사진 변수 이름 <br>
* <b>waitkey :</b> 창을 띄우고 기다리는지 그냥 가는지 판단 <br>
     - 0 : 창을 띄운 상태로 멈춤 <br>
     - 1 : 창을 띄우고 바로 다음 코드 실행 <br>
* <b>destroyAllWondows :</b> 창을 닫음 <br>
     - 1을 입력하면 사진창이 띄워졌다가 바로 닫힘 <br>
       그러나 실행이 매우 빠르므로 창이 안 열린 것으로 느낌 <br>

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
* <b>cv2.VideoCapture() :</b> 비디오 캡쳐 객체 생성 <br>
     - 입력 숫자 : 장치 인덱스로 어떤 카메라를 사용할 것인가를 뜻함 <br> 
     - 장치에 카메라 1개만 부착되어 있을 경우 : 0 (보통 기본 내장 카메라) <br>
     - 장치에 카메라가 2개 이상 부탁되어 있을 경우 : 0 (첫번째 웹캠), 1 (두번째 웹캠) <br>
* <b>cap.isOpen() :</b> 비디오 캡쳐 객체가 정상적으로 Open되었는지 확인
* <b>while True   :</b> 특정 키를 누를 때까지 무한 반복
* <b>ret, frame = cap.read() :</b> 비디오의 한 프레임씩 읽음
     - 프레임은 영상의 한 컷을 의미 <br>
     - 프레임을 제대로 읽으면 ret 변수에 True 입력됨 <br>
     - 프레임을 읽지 못하면 ret 변수에 False 입력됨 <br>
     - 프레임을 읽으면 읽은 프레임 스크린 데이터를 frame변수에 array값으로 입력됨 <br>
* <b>cv2.cvtColor() :</b> frame을 흑백으로 변환한다.
* <b>cap.release()  :</b> 오픈한 캡쳐 객체를 해제한다.
<br>
