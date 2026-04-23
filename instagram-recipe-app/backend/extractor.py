import base64
import json
import requests
import anthropic
from typing import Optional

client = anthropic.Anthropic()

RECIPE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Name of the dish"
        },
        "description": {
            "type": "string",
            "description": "Brief appetising description of the dish"
        },
        "servings": {
            "type": "string",
            "description": "Number of servings, e.g. '4 servings' or '2-3 people'"
        },
        "prep_time": {
            "type": "string",
            "description": "Preparation time, e.g. '15 mins'"
        },
        "cook_time": {
            "type": "string",
            "description": "Cooking time, e.g. '30 mins'"
        },
        "ingredients": {
            "type": "array",
            "description": "Complete list of ingredients with measurements",
            "items": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "Ingredient name, e.g. 'chicken breast', 'garlic cloves'"
                    },
                    "amount": {
                        "type": "string",
                        "description": "Quantity, e.g. '2', '1/2', '200', 'a handful'"
                    },
                    "unit": {
                        "type": "string",
                        "description": "Unit of measurement, e.g. 'cups', 'tbsp', 'g', 'ml', or empty string if countable"
                    },
                    "note": {
                        "type": "string",
                        "description": "Preparation note, e.g. 'finely chopped', 'room temperature', 'or to taste'"
                    }
                },
                "required": ["item", "amount", "unit", "note"],
                "additionalProperties": False
            }
        },
        "steps": {
            "type": "array",
            "description": "Step-by-step cooking instructions",
            "items": {
                "type": "object",
                "properties": {
                    "instruction": {
                        "type": "string",
                        "description": "Clear, actionable instruction for this step"
                    },
                    "tip": {
                        "type": "string",
                        "description": "Optional helpful tip or note for this step, or empty string"
                    }
                },
                "required": ["instruction", "tip"],
                "additionalProperties": False
            }
        }
    },
    "required": ["title", "description", "servings", "prep_time", "cook_time", "ingredients", "steps"],
    "additionalProperties": False
}


def get_reel_info(url: str) -> dict:
    """Extract metadata from Instagram reel using yt-dlp."""
    try:
        import yt_dlp
        opts = {
            'quiet': True,
            'no_warnings': True,
        }
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
    """Download image from URL and return as base64 JPEG string."""
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
    """Full pipeline: get reel info → analyse with Claude → return structured recipe."""

    info = get_reel_info(url)
    title = info.get('title', '')
    description = info.get('description', '')
    thumbnail_url = info.get('thumbnail', '')

    content = []

    # Add thumbnail image if we can fetch it
    if thumbnail_url:
        img_b64 = fetch_image_b64(thumbnail_url)
        if img_b64:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": img_b64
                }
            })

    # Build the text prompt
    text_parts = ["You are extracting a recipe from an Instagram cooking reel.\n\n"]

    if title:
        text_parts.append(f"Video title: {title}\n\n")

    if description:
        text_parts.append(f"Caption/Description:\n{description}\n\n")

    if not title and not description:
        text_parts.append(f"URL: {url}\n\n")
        text_parts.append("Use the thumbnail image to identify the dish and any visible ingredients.\n\n")

    text_parts.append("""Extract the COMPLETE recipe including:
- Every ingredient with exact quantities and units
- All preparation and cooking steps in the correct order
- Servings, prep time, and cook time if mentioned

If the caption contains a full recipe, extract it precisely.
If information is only in the image, identify the dish and list any visible ingredients.
Write step instructions as clear, friendly commands a home cook can follow.""")

    content.append({"type": "text", "text": "".join(text_parts)})

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=4096,
        output_config={
            "format": {
                "type": "json_schema",
                "schema": RECIPE_SCHEMA
            }
        },
        messages=[{"role": "user", "content": content}]
    )

    # Find the text block with JSON (output_config guarantees valid JSON)
    recipe_text = next(
        b.text for b in response.content if hasattr(b, 'text')
    )
    recipe_data = json.loads(recipe_text)

    return {
        **recipe_data,
        'source_url': url,
        'thumbnail_url': thumbnail_url,
    }
