from flask import Flask, request, jsonify, render_template
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

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
        "model": MISTRAL_MODEL,
        "messages": [{"role": "user", "content": message}],
    }

    response = requests.post(MISTRAL_URL, headers=headers, json=payload)
    if response.status_code != 200:
        return jsonify({"error": response.text}), response.status_code

    reply = response.json()["choices"][0]["message"]["content"]
    return jsonify({"response": reply})

# --- Audio upload / transcription ---
@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """
    Attend un fichier audio (wav/webm) et le transcrit avec Whisper
    """
    if "audio" not in request.files:
        return jsonify({"error": "Aucun fichier audio"}), 400

    audio_file = request.files["audio"]

    # Ici tu peux appeler Whisper API
    # Exemple fictif pour démonstration
    # Dans la vraie version, tu feras requests.post vers Whisper/Mistral Audio
    transcript = "Texte transcrit de l'audio"  # TODO : remplacer par vrai call API

    return jsonify({"transcript": transcript})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
