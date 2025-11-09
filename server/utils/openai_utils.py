import os
import json
import base64
from openai import OpenAI
from typing import Optional, Dict, Any


itemFields = ["category", "label", "color", "condition", "distinctive_features"] 
itemCategories = ["bottle", "book", "toy", "backpack", "bag", "cell_phone", "watch", "wallet", "key", "other"]


# Initialize OpenAI client lazily (only when API key is available)
def get_client() -> Optional[OpenAI]:
    """Get OpenAI client if API key is available"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def encode_image(image_path: str) -> str:
    """Encode image to base64 for OpenAI vision API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def parse_openai_json_response(content: str) -> Optional[Dict[str, Any]]:
    """
    Parse OpenAI API response content, handling markdown code blocks and JSON parsing.
    
    Args:
        content: Raw content string from OpenAI API response
        
    Returns:
        Parsed JSON dictionary or None if parsing fails
    """
    if not content or not content.strip():
        print(f"[ERROR] OpenAI returned empty response")
        return None
    
    # Remove markdown code blocks if present
    content = content.strip()
    if content.startswith("```"):
        # Remove ```json or ``` markers
        lines = content.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines)
    
    try:
        result = json.loads(content)
        return result
    except json.JSONDecodeError as json_err:
        print(f"[ERROR] OpenAI returned invalid JSON: {json_err}")
        print(f"[DEBUG] Response content: {content[:500]}")  # Log first 500 chars
        return None


def generate_item_description(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Generate a detailed description of a found item using OpenAI Vision API
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Dictionary with item description fields (category, color, condition, distinctive_features) or None if API call fails
    """
    try:
        client = get_client()
        if not client:
            print("[INFO] OpenAI API key not configured, skipping description generation")
            return None
            
        base64_image = encode_image(image_path)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that describes lost and found items. "
                        "Provide a concise, detailed description focusing on color, brand (if visible), "
                        "condition and distinctive features. Keep it short and concise. Do not include anything about the person "
                        "holding the item or the hand holding it. Ignore any other items that are not in the focus. "
                        "Always return a valid JSON object with the following fields: " + ", ".join(itemFields) + ". "
                        "Always use a generic item name for the label, if brand is know put it next to the label in parentheses."
                        "The category should be one of the following: " + ", ".join(itemCategories) + ". "
                        "If the item is not detected, set category to 'other' and provide what you can see."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Provide a detailed description "
                                "of this item that would help someone identify it if they lost it. "
                                "Keep it short and concise."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        
        content = response.choices[0].message.content
        result = parse_openai_json_response(content)
        if result:
            print(f"[DEBUG] OpenAI returned: {result}")
        return result
    except Exception as e:
        print(f"[ERROR] OpenAI description generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def search_items_with_llm(query: str, metadata: list) -> Dict[str, Any]:
    """
    Use LLM to help search through lost items metadata using natural language
    
    Args:
        query: Natural language search query
        metadata: List of item metadata records
        
    Returns:
        Dictionary with matched items and LLM reasoning
    """
    try:
        client = get_client()
        if not client:
            return {
                "reasoning": "OpenAI API key not configured",
                "matched_indices": [],
                "suggestions": [
                    "Please set OPENAI_API_KEY environment variable to enable LLM search"
                ]
            }
        
        # Format metadata for context
        items_context = "\n".join([
            (
                f"- {item.get('label', 'unknown')} found at "
                f"{item.get('timestamp', 'unknown time')}: "
                f"{item.get('image_url', 'no image')}"
            )
            for item in metadata[-20:]  # Last 20 items for context
        ])
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant for a lost and found system. "
                        "Help users find their lost items by analyzing queries and matching them "
                        "to item metadata. Be specific about which items match and why. "
                        "Always respond with valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"User query: '{query}'\n\n"
                        f"Available items:\n{items_context}\n\n"
                        "Which items match the user's query? Provide a JSON response with: "
                        "'reasoning' (explanation), 'matched_indices' (list of indices), "
                        "and 'suggestions' (helpful tips)."
                    )
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        result = parse_openai_json_response(content)
        if result:
            return result
        else:
            return {
                "reasoning": "Failed to parse OpenAI response",
                "matched_indices": [],
                "suggestions": []
            }
    except Exception as e:
        print(f"[ERROR] OpenAI search failed: {e}")
        return {
            "reasoning": "Search service temporarily unavailable",
            "matched_indices": [],
            "suggestions": []
        }
