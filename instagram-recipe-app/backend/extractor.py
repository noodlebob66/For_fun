import base64
import json
import os
import requests
from typing import Optional

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent?key=" + GEMINI_API_KEY
)

_PROMPT_TEMPLATE = """You are extracting a recipe from an Instagram cooking reel.

{title_line}{description_block}Extract the COMPLETE recipe and return it as JSON matching this exact structure:
{{
  "title": "Name of the dish",
  "description": "Brief appetising description",
  "servings": "e.g. 4 servings",
  "prep_time": "e.g. 15 mins",
  "cook_time": "e.g. 30 mins",
  "ingredients": [
    {{"item": "ingredient name", "amount": "quantity", "unit": "unit or empty string", "note": "prep note or empty string"}}
  ],
  "steps": [
    {{"instruction": "clear actionable step", "tip": "helpful tip or empty string"}}
  ]
}}

Rules:
- Extract every ingredient with exact quantities and units
- List all steps in the correct order as clear, friendly commands
- If the caption contains a full recipe, extract it precisely
- If information is only in the image, identify the dish and list visible ingredients
- Return ONLY the JSON object — no markdown, no extra text"""


def get_reel_info(url: str) -> dict:
    try:
        import yt_dlp
        opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', ''),
                'description': info.get('description', ''),
                'thumbnail': info.get('thumbnail', ''),
            }
    except Exception as e:
        print(f"yt-dlp error: {e}")
        return {'title': '', 'description': '', 'thumbnail': ''}


def fetch_image_b64(image_url: str) -> Optional[str]:
    try:
        resp = requests.get(image_url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        if resp.status_code == 200:
            return base64.b64encode(resp.content).decode('utf-8')
    except Exception as e:
        print(f"Image fetch error: {e}")
    return None


def extract_recipe(url: str) -> dict:
    info = get_reel_info(url)
    title = info.get('title', '')
    description = info.get('description', '')
    thumbnail_url = info.get('thumbnail', '')

    title_line = f"Video title: {title}\n\n" if title else ""
    description_block = f"Caption/Description:\n{description}\n\n" if description else ""

    prompt = _PROMPT_TEMPLATE.format(
        title_line=title_line,
        description_block=description_block,
    )

    parts = [{"text": prompt}]

    if thumbnail_url:
        img_b64 = fetch_image_b64(thumbnail_url)
        if img_b64:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img_b64,
                }
            })

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    resp = requests.post(GEMINI_URL, json=payload, timeout=60)
    resp.raise_for_status()

    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    recipe_data = json.loads(text)

    return {
        **recipe_data,
        'source_url': url,
        'thumbnail_url': thumbnail_url,
    }
