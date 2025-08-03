

동작 방식
1.  영상 저장 및 확인:
	•  최종 영상은 pending_videos/video_YYYY-MM-DD.mp4로 저장.
	•  사용자가 영상을 확인 후 checked_videos/checked_YYYY-MM-DD.mp4로 이름 변경하여 저장.
	•  다음 실행 시 checked_videos에서 checked가 포함된 가장 최근 영상을 선택.
2.  중복 제목 확인:
	•  uploaded_videos.txt에 업로드된 영상 제목 기록.
	•  업로드 전 제목이 파일에 있는지 확인, 중복 시 업로드 스킵.
3.  다국어 자막:
	•  한국어 자막: TTS 텍스트 기반으로 subtitles_ko.srt 생성.
	•  영어 자막: Helsinki-NLP/opus-mt-ko-en으로 번역하여 subtitles_en.srt 생성.
	•  유튜브 업로드 시 두 자막 파일 업로드, 언어 설정(ko, en).
4.  이메일 알림:
	•  업로드 성공 시 영상 링크와 파일명(checked_YYYY-MM-DD.mp4) 포함하여 이메일 전송.
JSON 파일 예시
raw_prompts/prompt_2025-08-03.json:

'''JSON
{
  "intro": "Today, we bring you the latest updates on technology.",
  "body": [
    "Summary of article 1...",
    "Summary of article 2..."
  ],
  "conclusion": "That's all for today's tech news. Stay tuned for more updates!",
  "youtube_video_count": 12345
}
'''



