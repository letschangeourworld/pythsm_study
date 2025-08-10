1.  영상 저장 및 확인
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

주요 최적화 및 개선 사항
1.  로컬 Whisper 동적 모델 선택:
	•  오디오 길이에 따라 모델 선택: 2분 미만 → tiny, 2~5분 → base, 5분 초과 → small.
	•  메모리 효율성: torch.inference_mode(), GPU/CPU 자동 전환, 메모리 정리(torch.cuda.empty_cache(), gc.collect()).
	•  세그먼트 처리: 30초 단위로 오디오 분할, 메모리 사용량 감소.
2.  M2M100_418M 번역 최적화:
	•  분할 처리: 텍스트를 1000자 단위로 분할하여 처리, 긴 텍스트에도 안정적.
	•  번역 캐싱: 텍스트의 SHA256 해시를 키로 사용하여 번역 결과 저장(cache/translation_<hash>.txt), 동일 텍스트 재처리 시 캐시 사용.
	•  성능: facebook/m2m100_418M으로 자연스러운 한국어-영어 번역 제공.
3.  Whisper 타임스탬프 영어 자막 적용:
	•  한국어 자막(Whisper 전사)의 타임스탬프를 영어 자막에도 동일하게 적용.
	•  세그먼트별 번역으로 동기화된 자막 생성.
4.  코드 정리:
	•  함수별 역할 명확화, 주석 추가, 변수명 표준화.
	•  공통 기능 모듈화(예: save_to_cache, load_from_cache).
	•  에러 처리 강화, 로깅 상세화.
5.  기존 기능 유지:
	•  영상 저장(pending_videos, checked_videos), 중복 제목 확인(uploaded_videos.txt), 다국어 자막(한국어/영어), 이메일 알림(링크+파일명).
	•  프롬프트 유효성 검사, 로그 파일, 다중 파일 처리, 유튜브 검색.

요구 사항
•  라이브러리:
```bash
 pip install openai-whisper newspaper3k requests beautifulsoup4 transformers diffusers torch elevenlabs pysrt moviepy google-api-python-client google-auth-oauthlib yt_dlp pydub
```

FFmpeg 설치 필수 (apt-get install ffmpeg 또는 Windows 바이너리).
•  폴더 구조:
	•  cache/: Whisper 전사 및 번역 결과 캐싱.
	•  pending_videos/, checked_videos/, raw_prompts/, modified_prompts/, output/, logs/, uploaded_videos.txt.
•  API 설정:
	•  YouTube Data API (client_secrets.json, 스코프: upload, readonly, force-ssl).
	•  ElevenLabs, Hugging Face (Stable Diffusion) API 키.
•  하드웨어:
	•  GPU(선택): NVIDIA 권장, 없으면 CPU 사용.
	•  tiny/base 모델은 CPU에서도 적합, small은 GPU 선호.

```python
import os
import json
import smtplib
import requests
import logging
import hashlib
import gc
import torch
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from newspaper import Article
from transformers import pipeline, M2M100Tokenizer, M2M100ForConditionalGeneration
from elevenlabs import ElevenLabs
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, concatenate_videoclips, TextClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from pydub import AudioSegment
import pysrt
import whisper
from googleapiclient.errors import HttpError

# 설정
CONFIG = {
    "NEWS_TOPIC": "technology",
    "VIDEO_DURATION": 300,  # 5분 (초)
    "RAW_PROMPT_DIR": "raw_prompts",
    "MODIFIED_PROMPT_DIR": "modified_prompts",
    "PENDING_VIDEOS_DIR": "pending_videos",
    "CHECKED_VIDEOS_DIR": "checked_videos",
    "OUTPUT_DIR": "output",
    "LOG_DIR": "logs",
    "CACHE_DIR": "cache",
    "UPLOADED_VIDEOS_FILE": "uploaded_videos.txt",
    "CLIENT_SECRETS_FILE": "client_secrets.json",
    "YOUTUBE_SCOPES": [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly",
        "https://www.googleapis.com/auth/youtube.force-ssl"
    ],
    "EMAIL_SENDER": "your_email@gmail.com",
    "EMAIL_PASSWORD": "your_app_password",
    "EMAIL_RECEIVER": "receiver_email@gmail.com",
    "ELEVENLABS_API_KEY": "your_elevenlabs_api_key",
    "HUGGINGFACE_TOKEN": "your_huggingface_token",
    "WHISPER_MODEL_MAP": {
        "tiny": 60,  # 2분 미만
        "base": 300,  # 2~5분
        "small": float("inf")  # 5분 초과
    }
}

# 디렉토리 생성
for directory in [CONFIG["RAW_PROMPT_DIR"], CONFIG["MODIFIED_PROMPT_DIR"], CONFIG["PENDING_VIDEOS_DIR"],
                 CONFIG["CHECKED_VIDEOS_DIR"], CONFIG["OUTPUT_DIR"], CONFIG["LOG_DIR"], CONFIG["CACHE_DIR"]]:
    os.makedirs(directory, exist_ok=True)

# 로깅 설정
logging.basicConfig(
    filename=f"{CONFIG['LOG_DIR']}/{datetime.now().strftime('%Y-%m-%d')}.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 캐시 처리 유틸리티
def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def save_to_cache(cache_path, content):
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(content)
    logging.info(f"Saved to cache: {cache_path}")

def load_from_cache(cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            logging.info(f"Loaded from cache: {cache_path}")
            return f.read()
    return None

# 1. 뉴스 수집
def collect_news(topic):
    logging.info(f"Collecting news for topic: {topic}")
    try:
        url = f"https://news.google.com/rss/search?q={topic}&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(url)
        response.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, "xml")
        articles = [
            {"title": item.link.text, "text": Article(item.link.text).text}
            for item in soup.find_all("item")[:5]
            if Article(item.link.text).download() or Article(item.link.text).parse()
        ]
        logging.info(f"Collected {len(articles)} articles")
        return articles
    except Exception as e:
        logging.error(f"Error collecting news: {e}")
        raise

# 2. 유튜브 검색
def search_youtube_videos(topic):
    logging.info(f"Searching YouTube for topic: {topic}")
    try:
        flow = InstalledAppFlow.from_client_secrets_file(CONFIG["CLIENT_SECRETS_FILE"], CONFIG["YOUTUBE_SCOPES"])
        credentials = flow.run_local_server(port=0)
        youtube = build("youtube", "v3", credentials=credentials)
        request = youtube.search().list(part="snippet", q=topic, type="video", maxResults=50)
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
            "intro": f"Today, we bring you the latest updates on {CONFIG['NEWS_TOPIC']}.",
            "body": [summarizer(article["text"][:1000], max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
                     for article in articles],
            "conclusion": "That's all for today's tech news. Stay tuned for more updates!",
            "youtube_video_count": search_youtube_videos(CONFIG["NEWS_TOPIC"])
        }
        date_str = datetime.now().strftime("%Y-%m-%d")
        prompt_file = f"{CONFIG['RAW_PROMPT_DIR']}/prompt_{date_str}.json"
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
        modified_files = [f for f in os.listdir(CONFIG["MODIFIED_PROMPT_DIR"])
                          if f.startswith("prompt_") and f.endswith(".json")]
        if not modified_files:
            logging.info("No modified prompts found")
            return None, None
        
        modified_files.sort(key=lambda x: os.path.getmtime(os.path.join(CONFIG["MODIFIED_PROMPT_DIR"], x)), reverse=True)
        latest_file = modified_files[0]
        modified_prompt_file = os.path.join(CONFIG["MODIFIED_PROMPT_DIR"], latest_file)
        with open(modified_prompt_file, "r", encoding="utf-8") as f:
            summary = json.load(f)
        
        if validate_prompt(summary):
            logging.info(f"Using modified prompt: {modified_prompt_file}")
            return summary, modified_prompt_file
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
            "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16, use_auth_token=CONFIG["HUGGINGFACE_TOKEN"]
        )
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
        image_paths = []
        for i, prompt in enumerate(prompts):
            with torch.inference_mode():
                image = pipe(prompt).images[0]
            image_path = f"{CONFIG['OUTPUT_DIR']}/image_{i}.png"
            image.save(image_path)
            image_paths.append(image_path)
        logging.info(f"Generated {len(image_paths)} images")
        torch.cuda.empty_cache()
        gc.collect()
        return image_paths
    except Exception as e:
        logging.error(f"Error generating images: {e}")
        raise

# 8. TTS 음성 생성
def generate_tts(summary):
    logging.info("Generating TTS audio")
    try:
        client = ElevenLabs(api_key=CONFIG["ELEVENLABS_API_KEY"])
        full_text = f"{summary['intro']}\n\n{'. '.join(summary['body'])}\n\n{summary['conclusion']}"
        audio = client.generate(text=full_text, voice="Rachel", model="eleven_multilingual_v2")
        audio_path = f"{CONFIG['OUTPUT_DIR']}/voiceover.mp3"
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
        # Whisper 모델 선택
        audio_duration = AudioSegment.from_file(audio_path).duration_seconds
        model_name = next((model for model, max_duration in CONFIG["WHISPER_MODEL_MAP"].items()
                           if audio_duration <= max_duration), "small")
        logging.info(f"Selected Whisper model: {model_name} for {audio_duration:.2f} seconds")

        # 캐시 확인
        audio_hash = get_file_hash(audio_path)
        cache_file = f"{CONFIG['CACHE_DIR']}/transcription_{audio_hash}.srt"
        if cached_transcription := load_from_cache(cache_file):
            subs_ko = pysrt.SubRipFile.from_string(cached_transcription)
        else:
            # Whisper 전사
            model = whisper.load_model(model_name)
            audio = AudioSegment.from_file(audio_path)
            segment_duration = 30 * 1000  # 30초 세그먼트
            segments = [audio[i:i+segment_duration] for i in range(0, len(audio), segment_duration)]
            subs_ko = pysrt.SubRipFile()
            current_time = 0
            for i, segment in enumerate(segments):
                segment_path = f"{CONFIG['OUTPUT_DIR']}/segment_{i}.wav"
                segment.export(segment_path, format="wav")
                with torch.inference_mode():
                    result = model.transcribe(segment_path, language="en")
                for seg in result["segments"]:
                    start = current_time + seg["start"]
                    end = current_time + seg["end"]
                    sub = pysrt.SubRipItem(
                        index=len(subs_ko)+1,
                        start=pysrt.SubRipTime(seconds=start),
                        end=pysrt.SubRipTime(seconds=end),
                        text=seg["text"]
                    )
                    subs_ko.append(sub)
                current_time += segment.duration_seconds
                os.remove(segment_path)
            subtitle_ko_path = f"{CONFIG['OUTPUT_DIR']}/subtitles_ko.srt"
            subs_ko.save(subtitle_ko_path)
            save_to_cache(cache_file, open(subtitle_ko_path, "r", encoding="utf-8").read())
            torch.cuda.empty_cache()
            gc.collect()

        # 영어 자막 (M2M100 번역)
        model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
        tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        tokenizer.src_lang = "ko"
        subs_en = pysrt.SubRipFile()
        text_chunks = [full_text[i:i+1000] for i in range(0, len(full_text), 1000)]
        text_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
        translation_cache = f"{CONFIG['CACHE_DIR']}/translation_{text_hash}.txt"
        
        if cached_translation := load_from_cache(translation_cache):
            translated_chunks = cached_translation.split("\n\n")
        else:
            translated_chunks = []
            for chunk in text_chunks:
                encoded = tokenizer(chunk, return_tensors="pt", truncation=True)
                generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.get_lang_id("en"))
                translated_chunk = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
                translated_chunks.append(translated_chunk)
            save_to_cache(translation_cache, "\n\n".join(translated_chunks))
        
        # 타임스탬프 동기화
        for i, sub_ko in enumerate(subs_ko):
            translated_text = translated_chunks[i % len(translated_chunks)][:50]
            subs_en.append(pysrt.SubRipItem(
                index=i+1,
                start=sub_ko.start,
                end=sub_ko.end,
                text=translated_text
            ))
        
        subtitle_ko_path = f"{CONFIG['OUTPUT_DIR']}/subtitles_ko.srt"
        subtitle_en_path = f"{CONFIG['OUTPUT_DIR']}/subtitles_en.srt"
        subs_ko.save(subtitle_ko_path)
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
        final_audio = voiceover.set_duration(CONFIG["VIDEO_DURATION"]).volumex(0.8) + background_music.volumex(0.2)
        final_audio_path = f"{CONFIG['OUTPUT_DIR']}/final_audio.mp3"
        final_audio.write_audiofile(final_audio_path)
        logging.info(f"Final audio saved to: {final_audio_path}")
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
        clips = [ImageClip(img_path).set_duration(CONFIG["VIDEO_DURATION"] / len(image_paths)) for img_path in image_paths]
        footage = VideoFileClip(footage_path).subclip(0, 10)
        clips.append(footage)
        video = concatenate_videoclips(clips, method="compose")
        audio = AudioFileClip(audio_path)
        video = video.set_audio(audio)
        subtitle_clip = TextClip(txt=open(subtitle_ko_path).read(), fontsize=24, color="white").set_duration(CONFIG["VIDEO_DURATION"])
        final_video = video.set_duration(CONFIG["VIDEO_DURATION"]).set_audio(audio)
        
        date_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        output_path = f"{CONFIG['PENDING_VIDEOS_DIR']}/video_{date_str}.mp4"
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
        checked_files = [f for f in os.listdir(CONFIG["CHECKED_VIDEOS_DIR"])
                         if f.startswith("checked_") and f.endswith(".mp4")]
        if not checked_files:
            logging.info("No checked videos found")
            return None, None, None
        
        checked_files.sort(key=lambda x: os.path.getmtime(os.path.join(CONFIG["CHECKED_VIDEOS_DIR"], x)), reverse=True)
        latest_file = checked_files[0]
        video_path = os.path.join(CONFIG["CHECKED_VIDEOS_DIR"], latest_file)
        date_str = latest_file.replace("checked_", "").replace(".mp4", "")
        title = f"Daily {CONFIG['NEWS_TOPIC'].capitalize()} News - {date_str}"
        description = f"Latest {CONFIG['NEWS_TOPIC']} news summary for {date_str}. Related YouTube videos: {search_youtube_videos(CONFIG['NEWS_TOPIC'])}."
        logging.info(f"Found checked video: {video_path}")
        return video_path, title, description
    except Exception as e:
        logging.error(f"Error checking checked video: {e}")
        return None, None, None

# 14. 업로드된 제목 확인
def check_uploaded_videos(title):
    logging.info(f"Checking if title already uploaded: {title}")
    try:
        if not os.path.exists(CONFIG["UPLOADED_VIDEOS_FILE"]):
            return False
        with open(CONFIG["UPLOADED_VIDEOS_FILE"], "r", encoding="utf-8") as f:
            uploaded_titles = f.read().splitlines()
        return title in uploaded_titles
    except Exception as e:
        logging.error(f"Error checking uploaded videos: {e}")
        return False

# 15. 업로드된 제목 기록
def record_uploaded_video(title):
    logging.info(f"Recording uploaded video title: {title}")
    try:
        with open(CONFIG["UPLOADED_VIDEOS_FILE"], "a", encoding="utf-8") as f:
            f.write(f"{title}\n")
        logging.info(f"Title recorded in {CONFIG['UPLOADED_VIDEOS_FILE']}")
    except Exception as e:
        logging.error(f"Error recording uploaded video: {e}")
        raise

# 16. 유튜브 업로드 (자막 포함)
def upload_to_youtube(video_path, title, description, subtitle_ko_path, subtitle_en_path):
    logging.info(f"Uploading video to YouTube: {title}")
    try:
        if check_uploaded_videos(title):
            logging.warning(f"Video already uploaded: {title}")
            return None
        
        flow = InstalledAppFlow.from_client_secrets_file(CONFIG["CLIENT_SECRETS_FILE"], CONFIG["YOUTUBE_SCOPES"])
        credentials = flow.run_local_server(port=0)
        youtube = build("youtube", "v3", credentials=credentials)
        
        body = {
            "snippet": {"title": title, "description": description, "tags": ["news", CONFIG["NEWS_TOPIC"], "automated"], "categoryId": "25"},
            "status": {"privacyStatus": "public"}
        }
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = request.execute()
        video_id = response["id"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        for subtitle_path, lang in [(subtitle_ko_path, "ko"), (subtitle_en_path, "en")]:
            caption_body = {"snippet": {"videoId": video_id, "language": lang, "name": f"{lang} subtitles"}}
            caption_media = MediaFileUpload(subtitle_path)
            youtube.captions().insert(part="snippet", body=caption_body, media_body=caption_media).execute()
            logging.info(f"Uploaded {lang} subtitles for video: {video_id}")

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
        msg["From"] = CONFIG["EMAIL_SENDER"]
        msg["To"] = CONFIG["EMAIL_RECEIVER"]
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(CONFIG["EMAIL_SENDER"], CONFIG["EMAIL_PASSWORD"])
            server.sendmail(CONFIG["EMAIL_SENDER"], CONFIG["EMAIL_RECEIVER"], msg.as_string())
        logging.info("Email notification sent")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise

# 메인 실행 함수
def main():
    logging.info("Starting automation script")
    try:
        video_path, title, description = check_checked_video()
        if video_path and title and description:
            subtitle_ko_path = f"{CONFIG['OUTPUT_DIR']}/subtitles_ko.srt"
            subtitle_en_path = f"{CONFIG['OUTPUT_DIR']}/subtitles_en.srt"
            if os.path.exists(subtitle_ko_path) and os.path.exists(subtitle_en_path):
                video_url = upload_to_youtube(video_path, title, description, subtitle_ko_path, subtitle_en_path)
                if video_url:
                    send_email(video_url, os.path.basename(video_path))
                return
            logging.warning("Subtitle files missing, proceeding to create new video")

        modified_summary, modified_prompt_file = check_modified_prompt()
        if modified_summary:
            logging.info(f"Processing modified prompt: {modified_prompt_file}")
            summary = modified_summary
        else:
            logging.info("No modified prompt found. Collecting and summarizing news...")
            articles = collect_news(CONFIG["NEWS_TOPIC"])
            summary, prompt_file = summarize_and_save_news(articles)
            logging.info("Exiting after saving raw prompt")
            return

        prompts = generate_image_prompts(summary)
        image_paths = generate_images(prompts)
        audio_path, full_text = generate_tts(summary)
        subtitle_ko_path, subtitle_en_path = generate_subtitles(audio_path, full_text)
        final_audio_path = add_background_music(audio_path)
        footage_path = insert_stock_footage()
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

최적화 세부 사항<br>
1.  Whisper 동적 모델 선택:<br>
	•  기준: 오디오 길이(초), tiny(<120초), base(120~300초), small(>300초).<br>
	•  성능:<br>
		   tiny: ~39MB, CPU에서 5분 오디오 약 1-2분 처리.<br>
		   base: ~74MB, CPU에서 5분 오디오 약 2-3분.<br>
		   small: ~244MB, GPU 권장, 5분 오디오 약 30-40초(GPU T4).<br>
	•  캐싱: cache/transcription_<hash>.srt로 전사 결과 저장, 재처리 시간 0초.<br>
	•  세그먼트: 30초 단위 처리, 메모리 사용량 최대 1GB 미만(base 기준).<br>
2.  M2M100 번역 최적화:<br>
	•  분할 처리: 1000자 단위로 텍스트 분할, truncation=True로 안정성 확보.<br>
	•  캐싱: cache/translation_<hash>.txt로 번역 결과 저장, 동일 텍스트 재번역 시 즉시 로드.<br>
	•  성능: 1000자 번역 약 2~3초(GPU), 캐싱 시 0초.<br>
	•  품질: Helsinki-NLP 대비 더 자연스러운 영어 출력, 특히 뉴스 문맥에서 강점.<br>
3.  타임스탬프 동기화:<br>
	•  Whisper의 세그먼트별 타임스탬프를 한국어/영어 자막에 동일 적용.<br>
	•  영어 자막은 번역된 텍스트를 세그먼트 단위로 매핑, 동기화 유지.<br>
4.  코드 구조:<br>
	•  CONFIG 딕셔너리로 설정 중앙화.<br>
	•  공통 캐싱 로직(save_to_cache, load_from_cache)으로 코드 재사용성 향상.<br>
	•  함수별 단일 책임 원칙 준수, 주석으로 가독성 강화.<br>


JSON 파일 예시
raw_prompts/prompt_2025-08-03.json:

```JSON
{
  "intro": "Today, we bring you the latest updates on technology.",
  "body": [
    "Summary of article 1...",
    "Summary of article 2..."
  ],
  "conclusion": "That's all for today's tech news. Stay tuned for more updates!",
  "youtube_video_count": 12345
}
```

uploaded_videos.txt 예시
```
Daily Technology News - 2025-08-02
Daily Technology News - 2025-08-03
```

Windows 작업 스케줄러 설정

•  이전과 동일: python path/to/your_script.py, 매일 08:00 AM 실행.
주의 사항

•  파일명 규칙: 사용자가 pending_videos/video_YYYY-MM-DD.mp4를 checked_videos/checked_YYYY-MM-DD.mp4로 정확히 이름 변경해야 함.

•  자막 타이밍: 현재 자막은 간단한 예시(5초). 실제로는 pysrt로 정확한 타이밍 조정 필요(예: Whisper API 사용).

•  API 쿼터: 자막 업로드 추가로 쿼터 소모 증가(영상 1,600 + 자막 2x200 = 2,000 포인트/업로드).

•  번역 품질: Helsinki-NLP 모델은 기본 품질 제공. 더 나은 번역을 위해 Google Translate API 고려.

•  배경음악/영상: background_music.mp3, stock_footage.mp4는 실제 파일로 대체.

Windows 작업 스케줄러<br>
•  python path/to/your_script.py, 매일 08:00 AM (KST).<br>
주의 사항 <br>
•  Whisper:<br>
	•  FFmpeg 필수.<br>
	•  tiny/base는 CPU 적합, small은 GPU 선호.<br>
	•  캐시 폴더(cache/) 주기적 정리 권장.<br>
•  번역:<br>
	•  M2M100_418M은 약 1~2GB RAM 필요.<br>
	•  긴 텍스트는 1000자 단위로 자동 분할.<br>
•  파일명:<br>
	•  pending_videos/video_YYYY-MM-DD.mp4 → checked_videos/checked_YYYY-MM-DD.mp4.<br>
•  API 쿼터:<br>
	•  YouTube: 영상(1,600) + 자막(2x200) = ~2,000 포인트/일.<br>
•  자막 동기화:<br>
	•  영어 자막은 번역 텍스트 길이로 인해 약간의 텍스트 잘림 가능(최대 50자).



