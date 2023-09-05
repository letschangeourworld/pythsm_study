'''
youtube_dl 라이브러리 안의 extractor 폴더의 youtube.py 프로그램을 수정해줘야 한다.
YoutubeVideo.py 파일을 확인해 볼 것
'''
'''
title          : 비디오 제목
url            : 비디오 URL
ext            : 비디오 파일 확장자
uploader       : 비디오 업로더
upload_date    : 비디오 업로드 날짜 (YYYYMMDD)
comment_count  : 해당 비디오 코멘트 숫자
width          : 비디오 width
height         : 비디오 height
playlist_index : 플레이 리스트 인덱스
playlist_title (string) : 플레이 리스트 제목
'''

import youtube_dl
import os

# 소스코드 현재폴더에 영상저장
os.path.join('./', '%(title)s.%(ext)s')

# 실행되는 폴더 안에 '영상제목.확장자'형식으로 다운로드
output_dir = os.path.join('./', '%(title)s.%(ext)s')

# 리스트 안에 여러 영상주소를 저장하면 한 번에 많은 영상을 다운로드 받을 수 있음
download_list = ['https://youtu.be/ViDAohrBEu4?si=_T2jBaTCg6NM3djg']
ydl_opt = {'outtmpl': output_dir, 'format': 'bestvideo/best'}

# 리스트 안에 있는 주소를 1개씩 가져와서 다운로드 시작
with youtube_dl.YoutubeDL(ydl_opt) as ydl:
  ydl.download(download_list)

print('다운로드가 완료되었습니다.')
