import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# =========================
# Gemini
# =========================

gemini = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

# =========================
# Telegram
# =========================

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# =========================
# Home
# =========================

@app.route("/")
def home():
    return "AI Agent is running! 🤖"


# =========================
# Ask API
# =========================

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json() or {}
    question = data.get("question", "")

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    try:

        print("QUESTION:", question)

        response = gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )

        answer = response.text or "AI-ը պատասխան չտվեց։"

        print("AI ANSWER:", answer)

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# Telegram Webhook
# =========================

@app.route("/telegram", methods=["POST"])
def telegram():

    update = request.get_json() or {}

    print("TELEGRAM UPDATE:", update)

    message = update.get("message")

    if not message:
        return jsonify({"ok": True})

    chat_id = message["chat"]["id"]
    question = message.get("text", "")

    if not question:
        return jsonify({"ok": True})

    try:

        print("QUESTION:", question)

        # Gemini
        response = gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )

        answer = response.text or "AI-ը պատասխան չտվեց։"

        print("GEMINI ANSWER:", answer)

        # Telegram
        telegram_response = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": answer
            },
            timeout=20
        )

        print(
            "TELEGRAM STATUS:",
            telegram_response.status_code
        )

        print(
            "TELEGRAM RESPONSE:",
            telegram_response.text
        )

    except Exception as e:

        print("ERROR:", repr(e))

        try:

            requests.post(
                f"{TELEGRAM_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "❌ AI-ի մոտ սխալ է տեղի ունեցել։"
                },
                timeout=20
            )

        except Exception as telegram_error:

            print(
                "TELEGRAM ERROR:",
                repr(telegram_error)
            )

    return jsonify({"ok": True})


# =========================
# Start server
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
