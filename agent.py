
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


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return "AI Agent is running! 🤖"


# =========================
# TELEGRAM
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

    try:

        # =========================
        # SHOW AVAILABLE GEMINI MODELS
        # =========================

        print("AVAILABLE GEMINI MODELS:")

        models = list(client.models.list())

        for model in models:
            print(model.name)

        # =========================
        # FIND A GEMINI MODEL
        # =========================

        model_name = None

        for model in models:
            name = model.name or ""

            if "gemini" in name.lower() and "generateContent" in str(
                getattr(model, "supported_actions", "")
            ):
                model_name = name
                break

        # Fallback
        if not model_name:

            for model in models:
                name = model.name or ""

                if "gemini" in name.lower():
                    model_name = name
                    break

        if not model_name:
            raise Exception("No Gemini model found for this API key.")

        print("USING MODEL:", model_name)

        # =========================
        # GEMINI
        # =========================

        response = client.models.generate_content(
            model=model_name,
            contents=text
        )

        answer = response.text

        if not answer:
            answer = "Չկարողացա պատասխան կազմել։"

        print("GEMINI ANSWER:", answer)

        # =========================
        # SEND TELEGRAM
        # =========================

        tg = requests.post(
            f"{TELEGRAM_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": answer
            },
            timeout=30
        )

        print("TELEGRAM STATUS:", tg.status_code)
        print("TELEGRAM RESPONSE:", tg.text)

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
