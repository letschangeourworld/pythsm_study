'''
youtube_dl 라이브러리 안의 extractor 폴더의 youtube.py 프로그램을 수정해줘야 한다.
위 파일코드를 확인해 볼 것
'''


import youtube_dl
import os

os.path.join('./', '%(title)s.%(ext)s')

# 실행되는 폴더 안에 '영상제목.확장자' 형식으로 다운로드
output_dir = os.path.join('./', '%(title)s.%(ext)s')

# 여러 영상을 받을 수 있고 플레이리스트도 가능함
download_list = ['https://youtu.be/ViDAohrBEu4?si=_T2jBaTCg6NM3djg']
ydl_opt = {'outtmpl': output_dir, 'format': 'bestvideo/best'}

with youtube_dl.YoutubeDL(ydl_opt) as ydl:
  ydl.download(download_list)

print('다운로드 완료했습니다.')
