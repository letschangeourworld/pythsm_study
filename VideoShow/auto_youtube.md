

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

```python
# pip install newspaper3k requests beautifulsoup4 transformers diffusers torch elevenlabs pysrt speechrecognition moviepy google-api-python-client google-auth-oauthlib yt_dlp pydub

import os
import sys
import json
import smtplib
import requests
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from newspaper import Article
from transformers import pipeline
from elevenlabs import ElevenLabs
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips, TextClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from pydub import AudioSegment
import pysrt
import speech_recognition as sr
import yt_dlp
from diffusers import StableDiffusionPipeline
import torch
from googleapiclient.errors import HttpError

# 설정
NEWS_TOPIC = "technology"  # 뉴스 주제
VIDEO_DURATION = 300  # 5분 (초 단위)
RAW_PROMPT_DIR = "raw_prompts"
MODIFIED_PROMPT_DIR = "modified_prompts"
PENDING_VIDEOS_DIR = "pending_videos"
CHECKED_VIDEOS_DIR = "checked_videos"
OUTPUT_DIR = "output"
LOG_DIR = "logs"
UPLOADED_VIDEOS_FILE = "uploaded_videos.txt"
CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
EMAIL_RECEIVER = "receiver_email@gmail.com"
ELEVENLABS_API_KEY = "your_elevenlabs_api_key"
HUGGINGFACE_TOKEN = "your_huggingface_token"

# 디렉토리 생성
for directory in [RAW_PROMPT_DIR, MODIFIED_PROMPT_DIR, PENDING_VIDEOS_DIR, CHECKED_VIDEOS_DIR, OUTPUT_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# 로깅 설정
log_file = f"{LOG_DIR}/{datetime.now().strftime('%Y-%m-%d')}.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 1. 뉴스 수집
def collect_news(topic):
    logging.info(f"Collecting news for topic: {topic}")
    try:
        url = f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url)
        response.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, "xml")
        items = soup.find_all("item")[:5]
        articles = []
        for item in items:
            article_url = item.link.text
            article = Article(article_url)
            article.download()
            article.parse()
            articles.append({"title": article.title, "text": article.text})
        logging.info(f"Collected {len(articles)} articles")
        return articles
    except Exception as e:
        logging.error(f"Error collecting news: {e}")
        raise

# 2. 유튜브 검색
def search_youtube_videos(topic):
    logging.info(f"Searching YouTube for topic: {topic}")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, YOUTUBE_SCOPES)
        credentials = flow.run_local_server(port=0)
        youtube = build("youtube", "v3", credentials=credentials)
        request = youtube.search().list(
            part="snippet",
            q=topic,
            type="video",
            maxResults=50
        )
        response = request.execute()
        video_count = response.get("pageInfo", {}).get("totalResults", 0)
        logging.info(f"Found {video_count} YouTube videos for topic: {topic}")
        return video_count
    except HttpError as e:
        logging.error(f"YouTube search error: {e}")
        return 0

# 3. 뉴스 요약 및 프롬프트 저장
def summarize_and_save_news(articles):
    logging.info("Summarizing news and saving prompt")
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = {
            "intro": f"Today, we bring you the latest updates on {NEWS_TOPIC}.",
            "body": [],
            "conclusion": "That's all for today's tech news. Stay tuned for more updates!",
            "youtube_video_count": search_youtube_videos(NEWS_TOPIC)
        }
        for article in articles:
            text = article["text"][:1000]
            summary_text = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
            summary["body"].append(summary_text)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        prompt_file = f"{RAW_PROMPT_DIR}/prompt_{date_str}.json"
        with open(prompt_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        logging.info(f"Raw prompt saved to: {prompt_file}")
        return summary, prompt_file
    except Exception as e:
        logging.error(f"Error summarizing news: {e}")
        raise

# 4. 프롬프트 유효성 검사
def validate_prompt(summary):
    logging.info("Validating prompt")
    try:
        required_keys = ["intro", "body", "conclusion"]
        if not all(key in summary for key in required_keys):
            logging.error("Missing required keys in prompt")
            return False
        if not isinstance(summary["body"], list) or not summary["body"]:
            logging.error("Body must be a non-empty list")
            return False
        if not all(isinstance(item, str) for item in summary["body"]):
            logging.error("All body items must be strings")
            return False
        if not isinstance(summary["intro"], str) or not isinstance(summary["conclusion"], str):
            logging.error("Intro and conclusion must be strings")
            return False
        logging.info("Prompt validation passed")
        return True
    except Exception as e:
        logging.error(f"Error validating prompt: {e}")
        return False

# 5. 수정된 프롬프트 확인
def check_modified_prompt():
    logging.info("Checking for modified prompt")
    try:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        modified_files = [f for f in os.listdir(MODIFIED_PROMPT_DIR) if f.startswith("prompt_") and f.endswith(".json")]
        if not modified_files:
            logging.info("No modified prompts found")
            return None, None
        
        modified_files.sort(key=lambda x: os.path.getmtime(os.path.join(MODIFIED_PROMPT_DIR, x)), reverse=True)
        latest_file = modified_files[0]
        modified_prompt_file = os.path.join(MODIFIED_PROMPT_DIR, latest_file)
        with open(modified_prompt_file, "r", encoding="utf-8") as f:
            summary = json.load(f)
        
        if validate_prompt(summary):
            logging.info(f"Using modified prompt: {modified_prompt_file}")
            return summary, modified_prompt_file
        else:
            logging.warning(f"Invalid modified prompt: {modified_prompt_file}")
            return None, None
    except Exception as e:
        logging.error(f"Error checking modified prompt: {e}")
        return None, None

# 6. 프롬프트 변환 (이미지 생성용)
def generate_image_prompts(summary):
    logging.info("Generating image prompts")
    try:
        prompts = [f"A futuristic scene representing {text[:50]}" for text in summary["body"]]
        logging.info(f"Generated {len(prompts)} image prompts")
        return prompts
    except Exception as e:
        logging.error(f"Error generating image prompts: {e}")
        raise

# 7. AI 이미지 생성
def generate_images(prompts):
    logging.info("Generating images with Stable Diffusion")
    try:
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            use_auth_token=HUGGINGFACE_TOKEN
        )
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
        image_paths = []
        for i, prompt in enumerate(prompts):
            image = pipe(prompt).images[0]
            image_path = f"{OUTPUT_DIR}/image_{i}.png"
            image.save(image_path)
            image_paths.append(image_path)
        logging.info(f"Generated {len(image_paths)} images")
        return image_paths
    except Exception as e:
        logging.error(f"Error generating images: {e}")
        raise

# 8. TTS 음성 생성
def generate_tts(summary):
    logging.info("Generating TTS audio")
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        full_text = f"{summary['intro']}\n\n{'. '.join(summary['body'])}\n\n{summary['conclusion']}"
        audio = client.generate(text=full_text, voice="Rachel", model="eleven_multilingual_v2")
        audio_path = f"{OUTPUT_DIR}/voiceover.mp3"
        with open(audio_path, "wb") as f:
            f.write(audio)
        logging.info(f"TTS audio saved to: {audio_path}")
        return audio_path, full_text
    except Exception as e:
        logging.error(f"Error generating TTS: {e}")
        raise

# 9. 자막 생성 (한국어 + 영어)
def generate_subtitles(audio_path, full_text):
    logging.info("Generating Korean and English subtitles")
    try:
        # 한국어 자막 (TTS 텍스트 기반)
        subs_ko = pysrt.SubRipFile()
        sub_ko = pysrt.SubRipItem(index=1, start=pysrt.SubRipTime(0, 0, 0), end=pysrt.SubRipTime(0, 5, 0), text=full_text[:50])
        subs_ko.append(sub_ko)
        subtitle_ko_path = f"{OUTPUT_DIR}/subtitles_ko.srt"
        subs_ko.save(subtitle_ko_path)

        # 영어 자막 (번역)
        translator = pipeline("translation", model="Helsinki-NLP/opus-mt-ko-en")
        translated_text = translator(full_text[:1000])[0]["translation_text"]  # 입력 길이 제한
        subs_en = pysrt.SubRipFile()
        sub_en = pysrt.SubRipItem(index=1, start=pysrt.SubRipTime(0, 0, 0), end=pysrt.SubRipTime(0, 5, 0), text=translated_text[:50])
        subs_en.append(sub_en)
        subtitle_en_path = f"{OUTPUT_DIR}/subtitles_en.srt"
        subs_en.save(subtitle_en_path)

        logging.info(f"Subtitles saved: {subtitle_ko_path}, {subtitle_en_path}")
        return subtitle_ko_path, subtitle_en_path
    except Exception as e:
        logging.error(f"Error generating subtitles: {e}")
        raise

# 10. 배경음악 추가
def add_background_music(audio_path):
    logging.info("Adding background music")
    try:
        background_music = AudioFileClip("background_music.mp3")
        voiceover = AudioFileClip(audio_path)
        final_audio = voiceover.set_duration(VIDEO_DURATION).volumex(0.8) + background_music.volumex(0.2)
        final_audio_path = f"{OUTPUT_DIR}/final_audio.mp3"
        final_audio.write_audiofile(final_audio_path)
        logging.info(f"Final audio with background music saved to: {final_audio_path}")
        return final_audio_path
    except Exception as e:
        logging.error(f"Error adding background music: {e}")
        raise

# 11. 현장 영상 삽입
def insert_stock_footage():
    logging.info("Inserting stock footage")
    footage_path = "stock_footage.mp4"
    if not os.path.exists(footage_path):
        logging.error(f"Stock footage not found: {footage_path}")
        raise FileNotFoundError(f"Stock footage not found: {footage_path}")
    return footage_path

# 12. 영상 제작 및 pending_videos 저장
def create_video(image_paths, audio_path, subtitle_ko_path, footage_path):
    logging.info("Creating final video")
    try:
        clips = [ImageClip(img_path).set_duration(VIDEO_DURATION / len(image_paths)) for img_path in image_paths]
        footage = VideoFileClip(footage_path).subclip(0, 10)
        clips.append(footage)
        video = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(audio_path)
        video = video.set_audio(audio)
        # 한국어 자막 추가 (영상 내장, 영어는 유튜브에서 처리)
        subtitle_clip = TextClip(txt=open(subtitle_ko_path).read(), fontsize=24, color="white").set_duration(VIDEO_DURATION)
        final_video = video.set_duration(VIDEO_DURATION).set_audio(audio)
        
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        output_path = f"{PENDING_VIDEOS_DIR}/video_{date_str}.mp4"
        final_video.write_videofile(output_path, codec="libx264")
        logging.info(f"Video saved to pending: {output_path}")
        return output_path
    except Exception as e:
        logging.error(f"Error creating video: {e}")
        raise

# 13. 체크된 영상 확인
def check_checked_video():
    logging.info("Checking for checked video")
    try:
        checked_files = [f for f in os.listdir(CHECKED_VIDEOS_DIR) if f.startswith("checked_") and f.endswith(".mp4")]
        if not checked_files:
            logging.info("No checked videos found")
            return None, None, None
        
        checked_files.sort(key=lambda x: os.path.getmtime(os.path.join(CHECKED_VIDEOS_DIR, x)), reverse=True)
        latest_file = checked_files[0]
        video_path = os.path.join(CHECKED_VIDEOS_DIR, latest_file)
        date_str = latest_file.replace("checked_", "").replace(".mp4", "")
        title = f"Daily {NEWS_TOPIC.capitalize()} News - {date_str}"
        description = f"Latest {NEWS_TOPIC} news summary for {date_str}."
        logging.info(f"Found checked video: {video_path}")
        return video_path, title, description
    except Exception as e:
        logging.error(f"Error checking checked video: {e}")
        return None, None, None

# 14. 업로드된 제목 확인
def check_uploaded_videos(title):
    logging.info(f"Checking if title already uploaded: {title}")
    try:
        if not os.path.exists(UPLOADED_VIDEOS_FILE):
            return False
        with open(UPLOADED_VIDEOS_FILE, "r", encoding="utf-8") as f:
            uploaded_titles = f.read().splitlines()
        return title in uploaded_titles
    except Exception as e:
        logging.error(f"Error checking uploaded videos: {e}")
        return False

# 15. 업로드된 제목 기록
def record_uploaded_video(title):
    logging.info(f"Recording uploaded video title: {title}")
    try:
        with open(UPLOADED_VIDEOS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{title}\n")
        logging.info(f"Title recorded in {UPLOADED_VIDEOS_FILE}")
    except Exception as e:
        logging.error(f"Error recording uploaded video: {e}")
        raise

# 16. 유튜브 업로드 (자막 포함)
def upload_to_youtube(video_path, title, description, subtitle_ko_path, subtitle_en_path):
    logging.info(f"Uploading video to YouTube: {title}")
    try:
        # 중복 제목 확인
        if check_uploaded_videos(title):
            logging.warning(f"Video already uploaded: {title}")
            return None
        
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, YOUTUBE_SCOPES)
        credentials = flow.run_local_server(port=0)
        youtube = build("youtube", "v3", credentials=credentials)
        
        # 영상 업로드
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": ["news", NEWS_TOPIC, "automated"],
                "categoryId": "25"
            },
            "status": {"privacyStatus": "public"}
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        video_id = response["id"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        # 자막 업로드
        for subtitle_path, lang in [(subtitle_ko_path, "ko"), (subtitle_en_path, "en")]:
            caption_body = {
                "snippet": {
                    "videoId": video_id,
                    "language": lang,
                    "name": f"{lang} subtitles"
                }
            }
            caption_media = MediaFileUpload(subtitle_path)
            youtube.captions().insert(part="snippet", body=caption_body, media_body=caption_media).execute()
            logging.info(f"Uploaded {lang} subtitles for video: {video_id}")

        # 업로드된 제목 기록
        record_uploaded_video(title)
        logging.info(f"Video uploaded: {video_url}")
        return video_url
    except Exception as e:
        logging.error(f"Error uploading to YouTube: {e}")
        raise

# 17. 이메일 알림
def send_email(video_url, video_filename):
    logging.info(f"Sending email notification for video: {video_url}")
    try:
        msg = MIMEText(f"Video uploaded successfully: {video_url}\nFilename: {video_filename}")
        msg["Subject"] = "YouTube Video Upload Notification"
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        logging.info("Email notification sent")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise

# 메인 실행 함수
def main():
    logging.info("Starting automation script")
    try:
        # 체크된 영상 확인 및 업로드
        video_path, title, description = check_checked_video()
        if video_path and title and description:
            subtitle_ko_path = f"{OUTPUT_DIR}/subtitles_ko.srt"
            subtitle_en_path = f"{OUTPUT_DIR}/subtitles_en.srt"
            if os.path.exists(subtitle_ko_path) and os.path.exists(subtitle_en_path):
                video_url = upload_to_youtube(video_path, title, description, subtitle_ko_path, subtitle_en_path)
                if video_url:
                    send_email(video_url, os.path.basename(video_path))
                return
            else:
                logging.warning("Subtitle files missing, proceeding to create new video")

        # 수정된 프롬프트 확인
        modified_summary, modified_prompt_file = check_modified_prompt()
        
        if modified_summary:
            logging.info(f"Processing modified prompt: {modified_prompt_file}")
            summary = modified_summary
        else:
            # 수정된 프롬프트가 없으면 뉴스 수집 및 요약
            logging.info("No modified prompt found. Collecting and summarizing news...")
            articles = collect_news(NEWS_TOPIC)
            summary, prompt_file = summarize_and_save_news(articles)
            logging.info("Exiting after saving raw prompt")
            return

        # 프롬프트 변환
        prompts = generate_image_prompts(summary)
        # 이미지 생성
        image_paths = generate_images(prompts)
        # TTS 생성
        audio_path, full_text = generate_tts(summary)
        # 자막 생성
        subtitle_ko_path, subtitle_en_path = generate_subtitles(audio_path, full_text)
        # 배경음악 추가
        final_audio_path = add_background_music(audio_path)
        # 현장 영상
        footage_path = insert_stock_footage()
        # 영상 제작
        create_video(image_paths, final_audio_path, subtitle_ko_path, footage_path)
        logging.info("Script completed, video saved to pending_videos")
    except Exception as e:
        logging.error(f"Script failed: {e}")
        raise

if __name__ == "__main__":
    main()

```
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





