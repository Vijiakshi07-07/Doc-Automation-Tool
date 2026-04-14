import os
from groq import Groq
from dotenv import load_dotenv

# This line reads your .env file and loads the API key into the program
# It looks for a file called .env in your project root folder
load_dotenv()


def get_groq_client():
    """
    Create and return a Groq client using the API key from .env
    This function is the ONLY place in the entire project that touches the API key.
    """
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found! Make sure your .env file exists "
            "and contains: GROQ_API_KEY=your_key_here"
        )

    return Groq(api_key=api_key)


def generate_glossary_definition(acronym, expansion):
    """
    Given an acronym and its expansion, ask the AI to generate
    a clear one-sentence definition suitable for a glossary.

    Example:
        acronym   = 'API'
        expansion = 'Application Programming Interface'
        returns   = 'A set of rules and protocols that allows different
                     software applications to communicate with each other.'
    """
    client = get_groq_client()

    prompt = f"""You are a technical documentation assistant.
Write a single clear sentence definition for the following term, suitable for a glossary in a technical document.

Term: {acronym} ({expansion})

Rules:
- One sentence only
- No bullet points
- Do not start with the acronym itself
- Keep it simple and easy to understand
- Do not add any extra explanation or notes

Definition:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=100
    )

    # Extract just the text from the response
    definition = response.choices[0].message.content.strip()
    return definition


def generate_image_description(surrounding_text):
    """
    Given the text around a screenshot or table in the document,
    ask the AI to generate a suitable caption/description.

    surrounding_text = the paragraph just before the image or table
    """
    client = get_groq_client()

    prompt = f"""You are a technical documentation assistant.
Based on the following surrounding text from a document, write a short one-sentence description 
that could be used as a caption for a screenshot or table that appears at this location.

Surrounding text: {surrounding_text}

Rules:
- One sentence only
- Start with 'Figure shows' or 'Table shows'
- Keep it clear and professional
- No extra notes or explanation

Caption:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=60
    )

    description = response.choices[0].message.content.strip()
    return description