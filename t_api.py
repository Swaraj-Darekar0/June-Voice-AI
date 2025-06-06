import os
import wave
import time
import numpy as np
import pyaudio
import tempfile
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Setup model cache
model_cache_dir = os.path.join(os.getcwd(), 'stt_model')
if not os.path.exists(model_cache_dir):
    os.makedirs(model_cache_dir)
os.environ['HF_HOME'] = model_cache_dir

from faster_whisper import WhisperModel

# Init FastAPI app
app = FastAPI()

# Load the whisper model
model = WhisperModel("Systran/faster-whisper-medium.en", device="cpu", compute_type="int8")

# Audio recording configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
SILENCE_THRESHOLD = 500
SILENCE_LIMIT = 1.5  # seconds

# Store path of latest recorded audio
latest_audio_path = None

def get_volume(data):
    audio_data = np.frombuffer(data, dtype=np.int16)
    rms = np.sqrt(np.mean(np.square(audio_data)))
    return rms

def record_audio_to_wav():
    global latest_audio_path

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("Recording started. Speak...")
    frames = []
    silent_chunks = 0
    silence_chunks_limit = int(SILENCE_LIMIT * RATE / CHUNK)

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        rms = get_volume(data)

        if rms < SILENCE_THRESHOLD:
            silent_chunks += 1
        else:
            silent_chunks = 0

        if silent_chunks > silence_chunks_limit:
            print("Silence detected. Stopping.")
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    # Write to temporary WAV file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav:
        latest_audio_path = tmp_wav.name
        with wave.open(tmp_wav, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

@app.post("/record")
def record():
    try:
        record_audio_to_wav()
        return JSONResponse(content={"message": "Recording done. Let me process."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/transcribe")
def transcribe():
    global latest_audio_path
    try:
        if not latest_audio_path or not os.path.exists(latest_audio_path):
            return JSONResponse(status_code=400, content={"error": "No audio recorded."})

        segments, _ = model.transcribe(latest_audio_path)
        full_text = " ".join([segment.text for segment in segments])

        # Optionally delete the file after use
        os.remove(latest_audio_path)
        latest_audio_path = None

        return JSONResponse(content={"transcription": full_text})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
