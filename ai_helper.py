import logging
from config import GEMINI_API_KEY
from google import genai
from google.genai import types

client = None
if GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logging.error(f"Failed to initialize GenAI client: {e}")

# Store chat sessions per user ID
user_chats = {}

async def get_ai_response(prompt: str, user_name: str, user_id: int) -> str:
    if not client:
        return "Произошла ошибка (API ключ не настроен)."
        
    # Read the detailed system instructions from file
    try:
        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            base_instruction = f.read()
    except Exception as e:
        logging.error(f"Failed to read system_prompt.txt: {e}")
        base_instruction = "Ты AI-Ментор курса Кирилла Орещенко. Помогай ученикам."

    # Add specific context for the current user
    system_instruction = (
        f"{base_instruction}\n\n"
        f"--- ВАЖНЫЙ ТЕКУЩИЙ КОНТЕКСТ ---\n"
        f"Имя ученицы, с которой ты сейчас общаешься: {user_name}.\n"
        f"Обязательно обращайся к ней по имени, если это уместно, и помни все правила выше."
    )
    
    try:
        if user_id not in user_chats:
            user_chats[user_id] = client.aio.chats.create(
                model='gemini-2.5-flash',
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
        
        chat = user_chats[user_id]
        response = await chat.send_message(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Error calling Gemini API: {e}")
        return "Произошла ошибка при обращении к нейросети."

def clear_chat_history(user_id: int):
    if user_id in user_chats:
        del user_chats[user_id]
