'''
유투브 데이터 형식변경으로 라이브러리 일부 프로그램도 변경해 업데이트해줘야 에러를 막을 수 있다.
라이브러리가 친절하게 버전 업데이트해주면 좋겠지만 그렇지 않은 경우에는 직접 고쳐야 한다.

[1]
pip로 youtube_dl을 설치한 후, 라이브러리 저장되어 있는 폴더로 찾아가서
Lib > site-packages > youtube_dl > extractor > youtube.py 파일을 찾아서 Notepad 같은 데에서 연 다음,
찾기(ctrl+F)로 'uploader_id': self. 문구를 입력하여 다음 부분을 찾는다.

'uploader_id': self._search_regex(r'/(?:channel/|user/|@)([^/?&#]+)',owner_profile_url,'uploader id', default=None, fatal=False) if owner_profile_url else None
위에서 다음 부분으로 붙여넣어 바꿔치기 한다.
r'/(?:channel/|user/|@)([^/?&#]+)',owner_profile_url,'uploader id', default=None, fatal=False
그리고 나서 저장한다.

[2]
pafy 라이브러리 저장되어 있는 폴더로 찾아가서,
Lib > site-packages >pafy > backend_youtube_dl.py 파일을 찾아서 Notepad에서 연 다음,
찾기(ctrl+F)로 self._likes 문구를 입력하여 다음 부분을 찾는다.

self._likes = self._ydl_info['like_count']
self._dislikes = self._ydl_info['dislike_count']

위 부분을 다음과 같이 수정한다.
self._likes = self._ydl_info.get('like_count',0)
self._dislikes = self._ydl_info.get('dislike_count',0)
그리고 나서 저장한다.
'''

import cv2
import pafy

url = 'https://youtu.be/ViDAohrBEu4?si=_T2jBaTCg6NM3djg'
video = pafy.new(url)
print(video)

best = video.getbest(preftype='mp4')        # 'webm','3gp'
print('best.resolution', best.resolution)

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(best.url)
 
# frame size
fmWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
fmHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_size = (fmWidth, fmHeight)
print('frame_size = ', frame_size)
 
# Codec 설정
# fourcc = cv2.VideoWriter_fourcc(*'DIVX')  # ('D','I','V','X')
fourcc = cv2.VideoWriter_fourcc(*'XVID')
 
# Create video file to save image
out1 = cv2.VideoWriter('./data/record0.mp4', fourcc, 20.0, frame_size)
out2 = cv2.VideoWriter('./data/record1.mp4', fourcc, 20.0, frame_size,isColor=False)

while True:
  ret, frame = cap.read()
  if not ret:
    break
    
  # Save in the video file
  out1.write(frame)
  
  # Convert image file
  gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  
  # Save in the video file
  out2.write(gray)
  
  # show image
  cv2.imshow('frame',frame)
  cv2.imshow('gray',gray)
  
  # ESC 키누르면 루프문 탈출
  if cv2.waitKey(1) == 27:
    break
    
cap.release()    # 카메라 해제
out1.release()   # 영상 해제
out2.release()   # 영상 해제
cv2.destroyAllWindows() # 윈도우창 닫기



