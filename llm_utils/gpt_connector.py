from openai import OpenAI
import logging
from time import sleep


def process_with_gpt(content, custom_prompt, api_key, max_retries=3, delay=1):
    """Process content with GPT API with retry logic"""
    client = OpenAI(api_key=api_key)
    try:
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that analyzes website content."},
                        {"role": "user", "content": f"{custom_prompt}\n\nContent to analyze:\n{content}"}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                    sleep_time = delay * (attempt + 1)
                    logging.warning(f"Rate limit reached. Retrying in {sleep_time} seconds...")
                    sleep(sleep_time)
                else:
                    raise        
    except Exception as e:
        logging.error(f"Failed to process content with GPT: {str(e)}")
        return f"Error: {str(e)}"