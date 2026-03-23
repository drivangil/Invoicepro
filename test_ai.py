import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Probando API Key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-flash-latest')
    response = model.generate_content("Hola, responde con la palabra 'OK' si recibes esto.")
    print(f"Respuesta IA: {response.text}")
except Exception as e:
    print(f"ERROR CRITICO: {e}")
