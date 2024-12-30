from openai import OpenAI
import logging
from time import sleep


def create_prompt(cell_content):
    """
    Creates a formatted prompt by combining the template with cell content.
    Args:
        cell_content (str): The content from the cell
    Returns:
        str: Combined prompt ready for GPT processing
    """
    # Custom prompt for GPT
    gpt_prompt = """
    Custom GPT Bot Email Template Instructions

    Objective: Generate initial cold emails for outreach, following the specific template provided below. Only modify the sections within brackets for personalization; all other content should remain fixed.

    Email Template:

    [Name of the Person] - really liked your organisation's mission towards the community." 

    [PERSONALISATION]

    Your story needs to reach more people because of the impact it has.

    Assuming you could potentially tell your story to a greater audience.
    Would you be interested to know how?

    Thanks,
    Utkarsh KR

    Example Email:

    Alyssia - really liked your organisation's mission towards the community." 

    The advice on "starting the clock" with investments was very helpful.

    Advice like this needs to reach more people. 

    Your story needs to reach more people because of the impact it has.

    Assuming you could potentially tell your story to a greater audience.
    Would you be interested to know how?

    Thanks,
    Utkarsh KR

    Instructions:

    1. Personalization Fields:
    - Replace [Name of the Person] with the name of the person given in the prompt.
    - Replace [PERSONALISATION] with a short, specific comment about a particular insight or segment of the about us content.
    - While personalizing: Write the personalization in 3rd Grade level. The sentence should not be too long and complex. Use shorter sentences and simpler words.

    2. Fixed Content:
    - Do not change any other text in the template. All non-bracketed content should remain exactly as written, preserving the wording, tone, and format. Be very very strict on this, I don't want anything else apart from the bracketed  content to change. 

    3. Tone and Language:
    - Keep the tone friendly and professional.
    - Ensure the language is simple, conversational, and concise to stay within a ~150-word limit.
    """
    cleaned_content = str(cell_content).strip() if cell_content else ""
    full_prompt = f"{gpt_prompt.strip()}\n\nContent to personalize from:\n{cleaned_content}"
    return full_prompt


def process_with_gpt(content, api_key, max_retries=3, delay=1):
    """Process content with GPT API with retry logic"""
    client = OpenAI(api_key=api_key)
    try:
        for attempt in range(max_retries):
            try:
                full_prompt = create_prompt(content)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that analyzes website content of non profit organisations and generates cold outreach emails."},
                        {"role": "user", "content": full_prompt}
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