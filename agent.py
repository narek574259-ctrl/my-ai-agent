import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# Gemini
gemini = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

# Telegram
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


@app.route("/")
def home():
    return "AI Agent is running! 🤖"


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json() or {}
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    try:
        response = gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )

        return jsonify({
            "answer": response.text
        })

    except Exception as e:
        print("Gemini error:", e)
        return jsonify({
            "error": "AI error"
        }), 500


@app.route("/telegram", methods=["POST"])
def telegram():
    update = request.get_json() or {}

    message = update.get("message")

    if not message:
        return jsonify({"ok": True})

    chat_id = message["chat"]["id"]
    question = message.get("text", "")

    if not question:
        return jsonify({"ok": True})

    try:
        # Gemini
        response = gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )

        answer = response.text

        # Telegram
        result = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": answer
            },
            timeout=20
        )

        print("Telegram response:", result.text)

    except Exception as e:
        print("ERROR:", e)

    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
