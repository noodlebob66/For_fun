import json
import os
import requests
from typing import Optional

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")

_PROMPT_TEMPLATE = """You are extracting a recipe from an Instagram cooking reel.

{title_line}{description_block}Return ONLY a JSON object with this exact structure (no markdown, no explanation):
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

Extract every ingredient with quantities and units. List all steps in order as clear, friendly commands."""


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


def extract_recipe(url: str) -> dict:
    info = get_reel_info(url)
    title = info.get('title', '')
    description = info.get('description', '')
    thumbnail_url = info.get('thumbnail', '')

    title_line = f"Video title: {title}\n\n" if title else ""
    description_block = f"Caption/Description:\n{description}\n\n" if description else ""

    if not title and not description:
        raise ValueError("Could not extract any text from this reel. Instagram may be blocking the request.")

    prompt = _PROMPT_TEMPLATE.format(
        title_line=title_line,
        description_block=description_block,
    )

    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )
    resp.raise_for_status()

    recipe_data = json.loads(resp.json()["response"])

    return {
        **recipe_data,
        'source_url': url,
        'thumbnail_url': thumbnail_url,
    }
