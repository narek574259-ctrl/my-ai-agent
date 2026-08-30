import os
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

# =========================
# SETTINGS
# =========================

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

client = genai.Client(
    api_key=GEMINI_API_KEY
)

TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# IMPORTANT:
# Use the model available to your account
GEMINI_MODEL = "gemini-3.6-flash"


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return "AI Agent is running! 🤖"


# =========================
# TELEGRAM WEBHOOK
# =========================

@app.route("/telegram", methods=["POST"])
def telegram():

    update = request.get_json(silent=True) or {}

    print("UPDATE:", update)

    message = update.get("message")

    if not message:
        return jsonify({"ok": True})

    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()

    if not chat_id or not text:
        return jsonify({"ok": True})

    print("USER:", text)
    print("USING MODEL:", GEMINI_MODEL)

    try:

        # =========================
        # GEMINI
        # =========================

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=text
        )

        answer = response.text

        if not answer:
            answer = "Չկարողացա պատասխան կազմել։"

        print("GEMINI:", answer)

        # =========================
        # TELEGRAM
        # =========================

        telegram_response = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": answer
            },
            timeout=30
        )

        print("TELEGRAM STATUS:", telegram_response.status_code)
        print("TELEGRAM RESPONSE:", telegram_response.text)

    except Exception as e:

        print("ERROR:", repr(e))

        try:
            requests.post(
                f"{TELEGRAM_URL}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "❌ Gemini-ի հետ սխալ է տեղի ունեցել։"
                },
                timeout=20
            )
        except Exception as telegram_error:
            print("TELEGRAM ERROR:", repr(telegram_error))

    return jsonify({"ok": True})


# =========================
# START
# =========================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
