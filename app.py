from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # autorise le frontend à se connecter depuis une autre origine (utile pour Render)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = "mistral-small-latest"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_input = request.json.get("message")

        if not user_input:
            return jsonify({"error": "Aucun message reçu"}), 400

        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": MISTRAL_MODEL,
            "messages": [{"role": "user", "content": user_input}],
        }

        response = requests.post(MISTRAL_URL, headers=headers, json=payload)

        if response.status_code != 200:
            return jsonify({"error": response.text}), response.status_code

        data = response.json()
        reply = data["choices"][0]["message"]["content"]

        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
