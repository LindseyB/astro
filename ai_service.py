"""
AI service for astrological analysis using Anthropic Claude
"""
import os
import json
import re
from anthropic import Anthropic
from config import logger

# Client setup for Anthropic API
token = os.environ.get("ANTHROPIC_TOKEN")
model = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 20000

# Initialize client as None, will be created when needed
client = None

def get_client():
    """Get or create Anthropic client with validation"""
    global client
    if client is None:
        if not token:
            raise ValueError("ANTHROPIC_TOKEN environment variable is not set")
        client = Anthropic(
            api_key=token,
            timeout=60.0  # 60 second timeout
        )
    return client


def call_ai_api(system_content, user_prompt, temperature=1.0):
    """
    Make AI API call with error handling

    Args:
        system_content (str): System prompt defining AI personality/role
        user_prompt (str): User message with chart data and request
        temperature (float): AI creativity level (default 1.0)

    Returns:
        str: AI response text or None on error
    """
    try:
        logger.debug("=== AI API CALL ===")
        api_client = get_client()
        response = api_client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            system=system_content,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        )

        # Log the response to console
        logger.debug("=== AI API RESPONSE ===")
        logger.debug(response.content[0].text)
        logger.debug("=== END RESPONSE ===")

        return response.content[0].text

    except Exception as e:
        # Handle various API errors gracefully
        error_type = type(e).__name__
        logger.error(f"AI Analysis Error ({error_type}): {str(e)}")
        return None


def stream_ai_api(system_content, user_prompt, temperature=1.0):
    """
    Make AI API call with streaming response

    Args:
        system_content (str): System prompt defining AI personality/role
        user_prompt (str): User message with chart data and request
        temperature (float): AI creativity level (default 1.0)

    Yields:
        str: Chunks of AI response text

    Returns:
        Generator yielding response chunks or error message
    """
    try:
        logger.debug("=== STREAMING AI API CALL ===")
        # Validate token before starting stream
        api_client = get_client()
        
        with api_client.messages.stream(
            model=model,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            system=system_content,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        ) as stream:
            for text in stream.text_stream:
                yield text

    except Exception as e:
        # Handle various API errors gracefully
        error_type = type(e).__name__
        logger.error(f"AI Streaming Error ({error_type}): {str(e)}")
        # pass through error to caller for handling
        raise e


def verify_song_exists(song_info):
    """
    Verify if a song suggestion is real using AI to double-check

    Args:
        song_info (str): Song information (title and artist)

    Returns:
        dict: {'is_real': bool, 'explanation': str}
    """
    try:
        verification_prompt = (
            f"You are a music expert. Check if this song is real:\n\n"
            f"{song_info}\n\n"
            f"Respond ONLY with a JSON object in this exact format:\n"
            f'{{"is_real": true/false, "explanation": "brief explanation"}}\n\n'
            f"If the song exists, is_real should be true. If it's made up or you're not confident it exists, is_real should be false."
        )

        system_content = "You are a precise music database expert. You only respond with valid JSON."

        api_client = get_client()
        response = api_client.messages.create(
            model=model,
            max_tokens=500,
            temperature=0.3,  # Lower temperature for factual verification
            system=system_content,
            messages=[
                {
                    "role": "user",
                    "content": verification_prompt
                }
            ]
        )

        result_text = response.content[0].text.strip()
        logger.debug(f"Verification response: {result_text}")
        
        # Extract JSON if wrapped in markdown code blocks using regex
        match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result_text, re.DOTALL)
        if match:
            result_text = match.group(1)
        result_text = result_text.strip()
        
        result = json.loads(result_text)
        return result

    except Exception as e:
        logger.error(f"Song verification error: {str(e)}")
        # If verification fails, assume it's suspicious
        return {'is_real': False, 'explanation': 'Could not verify song existence'}
