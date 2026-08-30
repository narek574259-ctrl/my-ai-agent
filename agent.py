import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# =========================
# GEMINI
# =========================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY is missing")

gemini = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================
# TELEGRAM
# =========================

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_TOKEN:
    raise Exception("TELEGRAM_BOT_TOKEN is missing")

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return "AI Agent is running! 🤖"


# =========================
# TEST GEMINI
# =========================

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json() or {}
    question = data.get("question", "").strip()

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

        print("GEMINI ANSWER:", answer)

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print("GEMINI ERROR:", repr(e))

        return jsonify({
            "error": "Gemini error"
        }), 500


# =========================
# TELEGRAM WEBHOOK
# =========================

@app.route("/telegram", methods=["POST"])
def telegram():

    update = request.get_json() or {}

    print("TELEGRAM UPDATE:", update)

    message = update.get("message")

    if not message:
        return jsonify({"ok": True})

    chat = message.get("chat", {})
    chat_id = chat.get("id")

    question = message.get("text", "").strip()

    if not chat_id or not question:
        return jsonify({"ok": True})

    try:

        print("USER MESSAGE:", question)

        # -------------------------
        # ASK GEMINI
        # -------------------------

        response = gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=question
        )

        answer = response.text or "Չկարողացա պատասխանել։"

        print("GEMINI ANSWER:", answer)

        # -------------------------
        # SEND TO TELEGRAM
        # -------------------------

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

        if not telegram_response.ok:
            print("TELEGRAM SEND ERROR")

    except Exception as e:

        print("TELEGRAM/GEMINI ERROR:", repr(e))

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
# START
# =========================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    print("Starting AI Agent...")
    print("Port:", port)

    app.run(
        host="0.0.0.0",
        port=port
    )
