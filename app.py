from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

# 🔑 Clés API Mistral
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
CHAT_MODEL = "mistral-small-latest"
TRANSCRIBE_MODEL = "mistral-audio-latest"  # modèle audio → texte
BASE_URL = "https://api.mistral.ai/v1"

# --- Page d'accueil ---
@app.route("/")
def home():
    return render_template("index.html")

# --- Chat texte ---
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Aucun message reçu"}), 400

    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": CHAT_MODEL,
        "messages": [{"role": "user", "content": message}],
    }

    response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload)
    if response.status_code != 200:
        return jsonify({"error": response.text}), response.status_code

    reply = response.json()["choices"][0]["message"]["content"]
    return jsonify({"response": reply})

# --- Transcription audio ---
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "audio" not in request.files:
        return jsonify({"error": "Aucun fichier audio"}), 400

    audio_file = request.files["audio"]

    files = {"file": (audio_file.filename, audio_file.stream, audio_file.mimetype)}
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}

    try:
        response = requests.post(
            f"{BASE_URL}/audio/transcriptions",
            headers=headers,
            files=files,
            data={"model": TRANSCRIBE_MODEL}
        )
        if response.status_code != 200:
            return jsonify({"error": response.text}), response.status_code

        transcript = response.json().get("text", "")
        return jsonify({"transcript": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
