# 한국어 성경
import json

with open('./bible/ko_ko.json', 'r', encoding='utf-8-sig') as f:
    bible_data = json.load(f)

bible_abbr_collect = []
for i in range(0, len(bible_data)):
    bible_abbr = list(bible_data[i].values())[0]
    bible_abbr_collect.append(bible_abbr)
print(len(bible_abbr_collect))
print(bible_abbr_collect)

# 요한복음 3:16 찾기
bible = "jo"
chapter = 3
bible_list_data = list(bible_data[chapter-1].values())
verse_from = 16
verse_to = 20
verse_to_all = len(bible_list_data[1][2])

for i in range(0, len(bible_data)):
    bible_list_data = list(bible_data[i].values())
    bible_abbr = list(bible_data[i].values())[0]
    if bible_abbr == bible:
        verse_text = bible_list_data[1][chapter-1][verse_from-1:verse_to-1]
        print(verse_text)
        break

# 영어 성경
import json

with open('./bible/en_bbe.json', 'r', encoding='utf-8-sig') as f:
    bible_data = json.load(f)

bible_abbr_collect = []
for i in range(0, len(bible_data)):
    bible_abbr = list(bible_data[i].values())[0]
    bible_abbr_collect.append(bible_abbr)
print(len(bible_abbr_collect))
print(bible_abbr_collect)

# 요한복음 3:16 찾기
bible = "jo"
chapter = 3
bible_list_data = list(bible_data[chapter-1].values())
verse_from = 16
verse_to = 20
verse_to_all = len(bible_list_data[1][2])

for i in range(0, len(bible_data)):
    bible_list_data = list(bible_data[i].values())
    bible_abbr = list(bible_data[i].values())[0]
    if bible_abbr == bible:
        verse_text = bible_list_data[1][chapter-1][verse_from-1:verse_to-1]
        print(verse_text)
        break

from transformers import pipeline
from datetime import datetime, timedelta

# 프롬프트 변환 (이미지 생성용)
def generate_image_prompts(summary):
    try:
        prompts = [f"A futuristic scene representing {text[:50]}" for text in summary["body"]]
        return prompts
    except Exception as e:
        print(f"Error generating image prompts: {e}")
        raise

# 이미지 생성을 위한 말씀요약 핵심어
RAW_PROMPT_DIR = "raw_prompts"
def summarize_and_save_verses(verse_text):
    try:
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        summary = {
            "intro": "Today, I bring you the bible verses.",
            "body": [],
            "conclusion": "That's all for today. Thank you!"
        }
        for verse in verse_text:
            summary_text = summarizer(verse, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
            summary["body"].append(summary_text)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        prompt_file = f"{RAW_PROMPT_DIR}/prompt_{date_str}.json"
        with open(prompt_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        prom = generate_image_prompts(summary)
        return summary, prompt_file, prom
    except Exception as e:
        print(f"Error summarizing verses: {e}")
        raise

summarize_and_save_verses(verse_text)

from diffusers import StableDiffusionPipeline
import torch

# torch_dtype=torch.float16,
# use_auth_token='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'
OUTPUT_DIR = "output"
def generate_images(prompts):
    try:
        pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")
        image_paths = []
        for i, prompt in enumerate(prompts):
            image = pipe(prompt).images[0]
            image_path = f"{OUTPUT_DIR}/image_{i}.png"
            image.save(image_path)
            image_paths.append(image_path)
        return image_paths
    except Exception as e:
        print(f"Error generating images: {e}")
        raise
generate_images(verse_text)

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
