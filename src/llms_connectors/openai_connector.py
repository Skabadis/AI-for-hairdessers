import os
from dotenv import load_dotenv
from openai import OpenAI

def get_openai_client():
    # Load variables from the .env file
    load_dotenv()
    # Access API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("The OpenAI API key must be set")
    # Connect to OpenAI
    client = OpenAI(api_key=openai_api_key)
    return client

# Function to interact with OpenAI's GPT-3.5 model
def chat(conversation_history, client):
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=conversation_history)
    return response.choices[0].message.content.strip()
