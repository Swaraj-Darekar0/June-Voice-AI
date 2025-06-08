import os
import wave
import pyaudio
import time
import numpy as np
import requests
from google import genai
import pygame
import io
import tempfile
import re
import json
import colorama
from colorama import Fore, Style

# Gemini setup
client = genai.Client(api_key="<YOUR-API-KEY>")

# Constants
T_API_URL = "http://localhost:8000/transcribe"
R_API_URL = "http://localhost:8000/record"

chat_log_filename = "chat_log.txt"
pygame.init()
pygame.mixer.init()

# Text styling for terminal
colorama.init()
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
NEON_GREEN = Fore.GREEN
RESET_COLOR = Style.RESET_ALL

# --- FLIRTY keyword triggers ---
FLIRTY_KEYWORDS = [
    "you are hot", "i love you", "your voice is sexy", "will you marry me",
    "you sound so beautiful","you sound kinda beautiful", "you’re cute", "hey baby", "are you single", "date me",
]

# --- DRAMATIC keyword triggers ---
DRAMATIC_KEYWORDS = [
     "suspense voice","suspenseful tone", "suspenseful voice" , "cinematic voice","suspense story" ,"story"]

Exit_KEYWORDS = [
    "exit now","i wanna exit","please exit"
]


def is_flirt_or_harass(text):
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in FLIRTY_KEYWORDS)

def exit_now(text):
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in Exit_KEYWORDS)

def is_dramatic(text):
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in DRAMATIC_KEYWORDS)

def generate_questions_from_gemini(transcribed_user_response, selected_voice):
    try:
        if selected_voice == "am_onyx":
            prompt = (
                f"User said: '{transcribed_user_response}'.Give a cocky ,savage and humorous response in the style of Andrew Tate if someone tries to flirt with his girl. Keep it under 200 characters. Make it bold, ruthless, and undeniable. "
            )
        else:
            prompt = (
                f"User said: '{transcribed_user_response}'. "
                "Reply appropriately in less than 200 characters."
            )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = response.text.strip()
        final_response = text[:200] if len(text) > 200 else text
        return final_response

    except Exception as e:
        print(f"Gemini Error: {e}")
        return "Sorry, there was an issue generating the response."

# --- TTS ---
def generate_and_play_audio(response_text, voice="af_bella"):
    try:
        tts_resp = requests.post(
            "http://localhost:8880/v1/audio/speech",
            json={
                "model": "kokoro",
                "input": response_text,
                "voice": voice,
                "response_format": "mp3",
                "speed": 1.0
            }
        )
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            f.write(tts_resp.content)
            temp_path = f.name

        pygame.mixer.music.load(temp_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error generating audio: {e}")

# --- Audio API ---
def Record_via_api():
    try:
        response = requests.post(R_API_URL)
        return response.status_code == 200
    except Exception as e:
        print(f"API request failed: {e}")
        return False

def transcribe_via_api():
    try:
        response = requests.post(T_API_URL)
        if response.status_code == 200:
            return response.json().get("transcription", "")
        else:
            print("Transcription API Error:", response.text)
            return ""
    except Exception as e:
        print(f"API request failed: {e}")
        return ""

def clean_exit(text):
    return re.sub(r'[^\w\s]', '', text).strip().lower()

# --- MAIN LOOP ---
def user_chatbot_conversation():
    conversation_history = []
    interaction_count = 0
    max_turns = 5

    while interaction_count < max_turns:
        print("Recording... Speak into the microphone.")
        if not Record_via_api():
            print("Recording failed. Try again.")
            continue

        print("Processing...")
        user_input = transcribe_via_api()
        cleaned_input = clean_exit(user_input)

        if not cleaned_input:
            print("No input detected. Try again.")
            continue

        if exit_now(user_input):
            print("Exiting conversation.")
            break

        print(CYAN + "You:", user_input + RESET_COLOR)
        conversation_history.append({"role": "user", "content": user_input})

        # Detect tone and assign voice
        if is_flirt_or_harass(user_input):
            selected_voice = "am_onyx"
        elif is_dramatic(user_input):
            selected_voice = "af_nicole"
        else:
            selected_voice = "af_bella"

        # Generate Gemini response
        print(MAGENTA + "Julie:" + RESET_COLOR)
        response_text = generate_questions_from_gemini(user_input, selected_voice)
        print(NEON_GREEN + response_text + RESET_COLOR)
        conversation_history.append({"role": "assistant", "content": response_text})

        generate_and_play_audio(response_text, voice=selected_voice)

        if selected_voice == "am_onyx":
            print("Flirt detected. Ending session.")
            break

        interaction_count += 1

    print("Session ended after", interaction_count, "interactions.")
    with open("conversation_history.json", "w", encoding="utf-8") as f:
        json.dump(conversation_history, f, ensure_ascii=False, indent=4)
    print("Conversation history saved to 'conversation_history.json'.")

user_chatbot_conversation()
