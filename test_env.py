from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv(r"C:\Users\Admin\OneDrive\Desktop\IBM\swara.env")
api_key = os.getenv("Groq_API_KEY")

print("Key starts with:", api_key[:10] if api_key else "None")

client = Groq(api_key=api_key)

# List available models first
models = client.models.list()
print("Available models:")
for m in models.data:
    print("-", m.id)

# Now use one that's actually available
response = client.chat.completions.create(
    model="openai/gpt-oss-20b",  # swap this once you see your real list
    messages=[{"role": "user", "content": "Say hello in one sentence."}]
)

print(response.choices[0].message.content)
# mental health chatbot that can provide support and resources for individuals struggling with mental health issues.
def mental_health_chatbot():
    

    print("Welcome to the Mental Health Chatbot!")
    print("Type 'exit' to end the conversation.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            print("Chatbot: Take care! Remember, seeking help is a sign of strength.")
            break
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": user_input}]
        )
        
        chatbot_reply = response.choices[0].message.content
        print("Chatbot:", chatbot_reply)