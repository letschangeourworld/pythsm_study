### ◈ Day1 : '21.5.12 (수)

* 실습코드 다운로드 (Pythsm 단톡방 공유) <br>
* pycharm 설치 (pycharm사이트에 가서 community용 무료 다운로드 설치) <br>
* 실습코드 파일을 가상환경 프로젝트 폴더로 이동 <br>
* 파이참(pycharm) 하단 터미널을 클릭 → 터미널 창에서 openCV 모듈 설치 <br>
     입력/실행 → <b>pip install opencv-contrib-python</b> <br>
* 주피터노트북을 사용해도 됨 <br>

<pre>
<code>
img = cv2.imread('aaa.jpg', 1)
</code>
</pre>

* <b>imread :</b> 이미지 불러오기 <br>
     - 좌측 인수 : 이미지 파일 경로입력 <br>
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

* <b>imshow :</b> 이미지를 창을 띄워 보여 줌 <br>
     - 좌측 인수 : 띄워지는 창 이름 <br>
     - 우측 인수 : 이미지가 들어 있는 변수 이름 입력 <br>
* <b>waitKey :</b> 창을 띄우고 기다리는지 그냥 가는지 판단 <br>
     - 0 : 창을 띄운 상태로 멈춤 <br>
     - 1 : 창을 띄우고 바로 다음 코드 실행 <br>
* <b>destroyAllWondows :</b> 창을 닫음 <br>
* waitKey(1)을 입력하면 이미지 창이 띄워졌다가 바로 닫힘. 그러나 실행이 매우 빠르므로 창이 안 열린 것으로 느껴짐<br>
<pre>
<code>
cv2.imwrite('aaa.jpg', img)
</code>
</pre>

* <b>imwrite :</b> 이미지를 내 컴퓨터에 저장
     - 좌측 인수 : 저장할 이미지 이름 입력
     - 우측 인수 : 이미지가 들어 있는 변수 이름 입력

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

* <b>VideoCapture() :</b> 비디오 캡쳐 객체 생성 <br>
     - 입력 숫자 : 장치 인덱스로 어떤 카메라를 사용할 것인가를 뜻함 <br> 
     - 장치에 카메라 1개만 부착되어 있을 경우 : 0 (보통 기본 내장 카메라) <br>
     - 장치에 카메라가 2개 이상 부탁되어 있을 경우 : 0 (첫번째 웹캠), 1 (두번째 웹캠) <br>
* <b>isOpen() :</b> 비디오 캡쳐 객체가 정상적으로 Open되었는지 확인
* <b>while True   :</b> 특정 키를 누를 때까지 무한 반복
* <b>ret, frame = cap.read() :</b> 비디오의 한 프레임씩 읽음
     - 프레임은 영상의 한 컷을 의미 <br>
     - 프레임을 제대로 읽으면 ret 변수에 True 입력됨 <br>
     - 프레임을 읽지 못하면 ret 변수에 False 입력됨 <br>
     - 프레임을 읽으면 읽은 프레임 스크린 데이터를 frame변수에 array값으로 입력됨 <br>
* <b>cvtColor() :</b> 색상 공간 변환 함수
     - 좌측 인수 : 프레임값이 들어 있는 변수 입력
     - 우측 인수 : array 프레임값을 칼라 또는 흑백 array값으로 변환
        - cv2.COLOR_BGR2GRAY : 원본 이미지 색상(COLOR_BGR)을 바꾸고자 하는 색상 공간(GRAY)으로 변환 <br>
        - 인수형태 <br>
              - BGR    : Blue,Green,Red 채널 <br>
              - BGRA   : Blue,Green,Red,Alpha 채널 <br>
              - RGB    : Red,Green,Blue 채널 <br>
              - RGBA   : Red,Green,Blue,Alpha 채널 <br>
              - GRAY   : 단일 채널 → 그레이 스케일 <br>
              - BGR565 : Blue,Green,Red 채널 → 16비트 이미지 <br>
              - XYZ    : X,Y,Z 채널 → CIE 1931 색공간 <br>
              - YCrCb  : Y,Cr,Cb 채널 → YCC(크로마) <br>
              - HSV    : Hue,Saturation,Value 채널 → 색상,채도,명도 <br>
              - Lab    : L,a,b 채널 → 반사율,색도1,색도2 <br>
              - Luv    : L,u,v 채널 → CIE Luv <br>
              - HLS    : Hue,Lightness,Saturation 채널 → 색상,밝기,채도 <br>
              - YUV    : Y,U,V 채널 → 밝기,색상1,색상2 <br>
              - BG,GB,RG : 디모자이킹 → 단일 색상 공간으로 변경 <br>
              - _EA    : 디모자이킹 → 가장자리 인식 <br>
              - _VNG   : 디모자이킹 → 그라데이션 사용 <br>

* <b>cap.release()  :</b> 오픈한 캡쳐 객체를 해제한다.
<br>


### ◈ Day2 : '21.5.18(화)

<pre>
<code>
import cv2 as cv
cap = cv.VideoCapture(0)
if cap.isOpened() == False:
    print("눈꺼풀이 안 열림")
    exit(1)
ret,img_frame = cap.read() # 눈이 정보를 읽는다
if ret == False:
    print("눈꺼풀 안에 눈이 정보를 못 읽음")
    exit(1)

# 영상을 저장할 때 해당 영상에 대한 코덱이 필요함
codec = cv.VideoWriter_fourcc(*'MJPG') # avi확장자에 맞는 코덱: MJPG
fps = 30.0   # fps : frame per second (초당 프레임수, 보통 30이 적당)
h,w = img_frame.shape[:2] # 인식한 프레임 정보 중 사이즈(높이,폭)를 가져온다
writer = cv.VideoWriter("output.avi",codec,fps,(w,h))
if writer.isOpened() == False: 
    print("녹화 준비가 안 됨")
    exit(1)

# 창을 띄워서 영상 플레이 시작 (무한루프문)
while(True):
    ret,img_frame = cap.read() # 눈꺼풀은 이미 열려 있으니까 정보를 읽는다
    if ret == False:
        print("눈이 정보를 못 읽음")
        break
    writer.write(img_frame) # 영상 녹화,저장
    cv.imshow('Color',img_frame) # 눈으로 본 것 창 띄워 보여주기
    # ESC키(아스키코드:27)누르면 무한루프문 빠져나가기
    key = cv.waitKey(1)
    if key == 27:
        break
cap.release() # 눈이 정보 읽는 것을 쉬게 하기
writer.release() # 영상 녹화/저장 준비하는 것을 쉬게 하기
cv.destroyAllWindows() # 창을 닫기

</code>
</pre>

* <b>추가 응용실습 문제</b> <br>
위에서 영상을 칼라영상으로 내 컴퓨터에 저장을 했는데, 흑백영상으로 저장해보자.<br>
내 컴퓨터에 저장된 흑백영상을 플레이 했을 때 정상적으로 플레이 돼야 한다.<br><br>
코덱은 아래 사이트 참고하기
http://www.fourcc.org/codecs.php


### 주피터노트북에서 코딩을 위한 vision이라는 이름으로 아나콘다 가상환경 만들기
1. prompt창 띄우기 : 시작 → Anaconda검색 → Anaconda prompt 실행
2. prompt창에 입력 (가상환경생성) : conda create -n vision python=3.6 라고 입력한 후 enter, 그리고 Y 입력
3. 가상환경 활성화 : activate vision
4. 넘파이 설치     : pip install numpy
5. openCV 설치    : pip install opencv-python
6. 주피터 설치     : pip install jupyter
7. 텐서플로우 설치 : pip install tensorflow==1.5.1

- 가상환경 활성화 상태에서 원하는 폴더로 가서 jupyter notebook 입력
- 가상환경 활성화 종료시 : deactivate 입력
- Mac북에서 가상환경 활성화시에는 이렇게 입력 : $ source activate vision
- Mac북에서 라이브러리 설치시 : pip3로 입력

### <2021년 SW coding practice>
<b>사물인식 최소면적 산출 프로그램 만들기</b><br>

당신은 직장에서 레이더 기술을 활용해 차량 주변의 장애물과 사물을 인식하는 프로그램을 만드는 업무를 담당하고 있다. <br>
당신은 다양한 입력 값들로 인식된 사물에 대해 최소 면적을 계산해보는 테스트를 하는 중이다. 이번 테스트의 조건은 다음과 같다. <br>

레이더를 통해 인식된 정보의 입력값은 평면에 N개의 점으로 주어진다. <br>
각각의 점들은 총 K개의 색깔 중 하나를 가지고 있다. <br>
각 점의 색깔은 {1, 2, …, K} 중의 한 정수로 표현된다.<br>

당신은 입력값으로 주어진 K개의 색깔 {1, 2, …, K}에 대해 해당 색깔을 가지는 점들을 적어도 하나씩 포함하는 <br>
사물 중 넓이가 가장 작은 것을 찾아서 그 넓이를 출력하는 프로그램을 작성하려고 한다. <br>
이 때, 각 점을 포함한 사물은 반드시 직사각형으로 인식된다. <br>

여기서 사물로 인식되는 직사각형은 네 변이 모두 수평 혹은 수직인 것에 한정하며, <br>
직사각형의 내부가 아닌 경계에 놓은 점들도 그 직사각형에 포함된다고 생각한다. <br>
직사각형의 가로 또는 세로의 길이가 0이 되어 선분 혹은 점으로 나타나는 경우도 직사각형의 한 경우로 생각하며 <br>
이런 경우 직사각형의(사물) 넓이는 0이다. (하나의 좌표에 여러 개의 점이 있을 수 있다) <br>

주어지는 입력값에 대해 K개의 색을 가진 점들을 적어도 하나씩 포함하는 사물(직사각형) 중 <br>
넓이가 가장 작은 것의 넓이를 출력하는 프로그램을 만들어 보자. <br>

(10점) 1 ≤ K ≤ 2 <br>
(15점) 1 ≤ N ≤ 10 <br>
(25점) 1 ≤ N ≤ 40 <br>
(50점) 추가 제약 조건 없음. <br>

<입력형식> <br>
입력으로 점의 개수인 자연수 N과 각 점들이 가질 수 있는 색깔의 총 개수인 자연수 K가 첫 줄에 주어진다. <br>
(1 ≤ N ≤ 100, 1 ≤ K ≤ 20) <br>
이후 N줄에는 입력으로 주어지는 점의 좌표(x, y)와 그 점의 색깔 k가 세 개의 정수 x, y, k로 각 줄에 주어진다. <br>
(-1,000 ≤ x, y ≤ 1,000, 1 ≤ k ≤ K) <br>

<출력형식> <br>
주어진 입력에 대해 K개의 색깔 {1, 2, …, K} 각각에 대해 해당 색깔을 가지는 점들을 <br>
적어도 하나씩 포함하는 사물(직사각형)중 넓이가 가장 작은 것을 찾아서 그 넓이를 정수 형태로 출력한다. <br>

<b> 1. 데이터 입력 (N, M) </b><br>
<pre>
<code>
N, K = map(int, input().split())
data = [list(map(int, input().split())) for _ in range(N)]
print(data)
</code>
</pre>

<출력>
<pre>
<code>
5 3
3 7 1
5 8 1
6 5 2
7 1 3
9 3 3
[[3, 7, 1], [5, 8, 1], [6, 5, 2], [7, 1, 3], [9, 3, 3]]
</code>
</pre>

<b> 2. 원데이터에서 색깔 분류 </b><br>
<pre>
<code>
arr = []
for i in range(K):
    arr.append([])
    for j in data:
        if j[2] == i+1:
            arr[i].append([j[0],j[1]])
print(arr)
</code>
</pre>


