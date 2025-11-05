import os
import json
import base64
from openai import OpenAI
from typing import Optional, Dict, Any

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


def generate_item_description(image_path: str, detected_label: str, confidence: float) -> Optional[str]:
    """
    Generate a detailed description of a found item using OpenAI Vision API
    
    Args:
        image_path: Path to the image file
        detected_label: The label detected by YOLO
        confidence: Detection confidence score
        
    Returns:
        Generated description or None if API call fails
    """
    try:
        client = get_client()
        if not client:
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
                        "holding the item or the hand holding it. Ignore any other items that are not in the focus."
                        "If the item is not detected, return 'No item detected'."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f"This is a detected {detected_label} "
                                f"(confidence: {confidence:.2%}). Provide a detailed description "
                                "of this item that would help someone identify it if they lost it."
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
            max_tokens=150
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] OpenAI description generation failed: {e}")
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
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"[ERROR] OpenAI search failed: {e}")
        return {
            "reasoning": "Search service temporarily unavailable",
            "matched_indices": [],
            "suggestions": []
        }
