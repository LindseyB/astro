"""
AI service for astrological analysis using Anthropic Claude
"""
import os
from anthropic import Anthropic
from config import logger

# Client setup for Anthropic API
token = os.environ.get("ANTHROPIC_TOKEN") or "default_token"
model = "claude-haiku-4-5-20251001"
MAX_TOKENS = 8192 # Max tokens for Claude models
client = Anthropic(
    api_key=token,
    timeout=60.0  # 60 second timeout
)


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
        response = client.messages.create(
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
