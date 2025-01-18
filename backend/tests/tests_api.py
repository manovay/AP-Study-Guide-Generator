import openai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_study_guide(prompt):
    try:
        # Updated API call
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model
            messages=[
                {"role": "system", "content": "You are a helpful assistant for generating study guides."},
                {"role": "user", "content": f"Create a study guide for: {prompt}"}
            ],
            temperature=0.7,  # Adjust creativity level
            max_tokens=500,  # Adjust token count as needed
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        raise Exception(f"Error generating study guide: {e}")