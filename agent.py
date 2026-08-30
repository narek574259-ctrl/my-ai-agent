import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY is missing")

client = genai.Client(api_key=GEMINI_API_KEY)

# Telegram
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_BOT_TOKEN is missing")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


@app.route("/")
def home():
    return "AI Agent is running! 🤖"


@app.route("/telegram", methods=["POST"])
def telegram():

    update = request.get_json() or {}

    print("TELEGRAM UPDATE:", update)

    message = update.get("message")

    if not message:
        return jsonify({"ok": True})

    chat_id = message.get("chat", {}).get("id")
    question = message.get("text", "").strip()

    if not chat_id or not question:
        return jsonify({"ok": True})

    try:

        print("USER MESSAGE:", question)

        # Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )

        answer = response.text

        print("GEMINI ANSWER:", answer)

        # Telegram
        result = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": answer
            },
            timeout=20
        )

        print("TELEGRAM STATUS:", result.status_code)
        print("TELEGRAM RESPONSE:", result.text)

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        try:
            requests.post(
                f"{TELEGRAM_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "❌ Gemini-ի մոտ սխալ է տեղի ունեցել։"
                },
                timeout=20
            )
        except Exception as telegram_error:
            print("TELEGRAM ERROR:", repr(telegram_error))

    return jsonify({"ok": True})


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
