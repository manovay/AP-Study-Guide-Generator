import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_study_guide(prompt):
    """
    Generate a study guide based on the given prompt.
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Create a detailed study guide for: {prompt}",
            max_tokens=500,
            temperature=0.7,
        )
        study_guide = response['choices'][0]['text'].strip()
        return study_guide
    except Exception as e:
        raise Exception(f"Error generating study guide: {e}")