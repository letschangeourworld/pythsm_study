

1.  영상 저장 및 확인:
	•  최종 생성된 영상을 유튜브에 업로드하기 전에 pending_videos 폴더에 저장.
	•  사용자가 확인 후 영상 파일명을 checked_YYYY-MM-DD 형식으로 변경하여 checked_videos 폴더에 저장.
	•  checked_videos 폴더에서 checked가 포함된 가장 최근 영상만 유튜브에 업로드.
2.  중복 제목 확인:
	•  유튜브 업로드 전 uploaded_videos.txt 파일을 확인하여 동일한 제목의 영상이 이미 업로드되었는지 확인.
	•  중복 제목이 없으면 업로드 진행, 업로드 후 제목을 uploaded_videos.txt에 기록.
3.  이메일 알림 개선:
	•  이메일에 유튜브 영상 링크와 함께 업로드된 영상 파일명을 포함.
4.  다국어 자막:
	•  자막을 한국어와 영어로 생성 (subtitles_ko.srt, subtitles_en.srt).
	•  한국어는 TTS 텍스트를 기반으로, 영어는 Hugging Face 번역 모델(Helsinki-NLP/opus-mt-ko-en)을 사용해 번역.
	•  유튜브 업로드 시 두 자막 파일을 함께 업로드.
5.  기존 기능 유지:
	•  프롬프트 유효성 검사, 로그 파일 생성, 다중 파일 처리, 유튜브 검색 기능 등은 이전 코드에서 유지.
요구 사항
•  추가 라이브러리:
	•  번역을 위해 transformers의 Helsinki-NLP/opus-mt-ko-en 모델 사용.
	•  기존 라이브러리: newspaper3k, requests, beautifulsoup4, transformers, diffusers, elevenlabs, pysrt, speechrecognition, moviepy, google-api-python-client, google-auth-oauthlib, yt_dlp, pydub.
•  폴더 구조:
	•  pending_videos/: 업로드 전 영상 저장.
	•  checked_videos/: 확인 후 checked로 이름 변경된 영상 저장.
	•  raw_prompts/, modified_prompts/, output/, logs/: 기존과 동일.
•  파일:
	•  uploaded_videos.txt: 업로드된 영상 제목 기록.
•  API 설정:
	•  YouTube Data API에 자막 업로드 권한 추가 (https://www.googleapis.com/auth/youtube.force-ssl).
	•  이전 답변의 API 설정(Google Cloud, ElevenLabs, Stable Diffusion 등) 필요.


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

<pre><code>
// JSON
{
  "intro": "Today, we bring you the latest updates on technology.",
  "body": [
    "Summary of article 1...",
    "Summary of article 2..."
  ],
  "conclusion": "That's all for today's tech news. Stay tuned for more updates!",
  "youtube_video_count": 12345
}
</code></pre>

Windows 작업 스케줄러 설정
•  이전과 동일: python path/to/your_script.py, 매일 08:00 AM 실행.
주의 사항
•  파일명 규칙: 사용자가 pending_videos/video_YYYY-MM-DD.mp4를 checked_videos/checked_YYYY-MM-DD.mp4로 정확히 이름 변경해야 함.
•  자막 타이밍: 현재 자막은 간단한 예시(5초). 실제로는 pysrt로 정확한 타이밍 조정 필요(예: Whisper API 사용).
•  API 쿼터: 자막 업로드 추가로 쿼터 소모 증가(영상 1,600 + 자막 2x200 = 2,000 포인트/업로드).
•  번역 품질: Helsinki-NLP 모델은 기본 품질 제공. 더 나은 번역을 위해 Google Translate API 고려.
•  배경음악/영상: background_music.mp3, stock_footage.mp4는 실제 파일로 대체.




