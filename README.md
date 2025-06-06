


# 🎙️ June – Voice-Driven AI Assistant (Gemini + Kokoro TTS)

June is an expressive voice-based assistant that listens to what you say, understands it using Whisper, thinks using Gemini (LLM), and speaks back using Kokoro TTS — with emotional tone detection and voice switching.

Whether you're asking a factual question, telling a suspense story, or getting flirty, June responds accordingly with different personalities and voices.

📹 **Demo Video:**

➡️ [Click to watch the demo](media/Live_video.mp4)
---

## 📌 Abstract

This project integrates:
- 🔊 Real-time voice input (recorded via FastAPI)
- 🧠 Gemini Flash for conversational responses
- 🎧 Faster-Whisper for speech-to-text transcription
- 🗣️ Kokoro TTS for real-time text-to-speech (Dockerized)
- 🧠 Context-based voice switching based on **flirt**, **drama**, or **neutral** tones

---

## ✨ Features

- 🎙️ Record your voice and transcribe it to text with `faster-whisper`
- 🧠 Get intelligent, concise replies from Google Gemini
- 🗣️ Hear June speak back using Kokoro TTS with emotion-aware voices
- 😏 Detect flirtatious or inappropriate prompts and reply in **Andrew Tate style**
- 🎬 Switch to cinematic/suspense voice when dramatic tones are detected
- 👩 Default warm assistant voice (af_bella)
- 🛑 Voice-commanded exit using phrases like “exit now”

---

### ⚙️ Installation & Setup

### 1. Clone the repo

```bash
git clone https://github.com/Swaraj-Darekar0/June-Voice-AI.git
cd June-Voice-AI

```
### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Kokoro TTS using Docker

Make sure Docker is installed and running. Then run:

```bash
docker run -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-cpu:latest # CPU, or:
docker run --gpus all -p 8880:8880 ghcr.io/remsky/kokoro-fastapi-gpu:latest  #NVIDIA GPU
```

This runs the Kokoro TTS engine locally on port `8880`.

### 4. Start FastAPI backend

In a new terminal window/tab:

```bash
uvicorn t_api:app --reload
```

This will expose:
* Increase/Decrease the threshold in `t_api.py` Depending on your mic 
* `POST /record` – records mic input until silence
* `POST /transcribe` – returns transcription of the latest recording

### 5. Start the main chatbot

In another terminal window:

```bash
python june.py
```

Now speak naturally, and Julie will:

* ✅ Respond with smart, relevant answers
* 😏 Switch to Andrew Tate tone if you flirt
* 🎬 Speak dramatically if you say *“tell me a suspense story”*
* 🛑 Exit if you say *“exit now”*

---


## 🧠 Tech Stack

| Component     | Technology                    |
| ------------- | ----------------------------- |
| ASR (Speech)  | `faster-whisper`              |
| LLM (Reply)   | `Gemini Flash` (Google API)   |
| Voice Synth   | `Kokoro TTS` via Docker       |
| Audio Input   | `PyAudio + FastAPI`           |
| Audio Output  | `pygame`                      |
| Emotion Logic | Custom keyword-based triggers |

---

## 📁 Project Structure

```bash
├── june.py           # Main assistant logic (conversation loop)
├── t_api.py          # FastAPI backend for record/transcribe
├── requirements.txt  # Python dependencies
├── conversation_history.json  # Saved logs
```

---

## 🔐 Notes

* Requires Gemini API key from Google.
* Make sure port `8880` is available for Kokoro TTS.
* All audio processing is local except Gemini requests.
* Latency depends upon your device power
---

## 👨‍💻 Author

Built by `Swaraj Darekar`,
Actively looking for internships in AI, conversational agents, and voice tech.
Feel free to fork, star, or reach out!

---

