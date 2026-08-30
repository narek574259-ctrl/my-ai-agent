
import os
import threading
import requests
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

gemini = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


@app.route("/")
def home():
    return "AI Agent is running! 🤖"


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    response = gemini.models.generate_content(
        model="gemini-3.6-flash",
        contents=question
    )

    return jsonify({
        "answer": response.text
    })


def telegram_loop():
    offset = None

    while True:
        try:
            params = {"timeout": 30}

            if offset is not None:
                params["offset"] = offset

            response = requests.get(
                f"{TELEGRAM_URL}/getUpdates",
                params=params,
                timeout=40
            )

            updates = response.json().get("result", [])

            for update in updates:
                offset = update["update_id"] + 1

                message = update.get("message")

                if not message or "text" not in message:
                    continue

                chat_id = message["chat"]["id"]
                question = message["text"]

                ai_response = gemini.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=question
                )

                answer = ai_response.text

                requests.post(
                    f"{TELEGRAM_URL}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": answer
                    },
                    timeout=20
                )

        except Exception as e:
            print("Telegram error:", e)


if __name__ == "__main__":
    threading.Thread(
        target=telegram_loop,
        daemon=True
    ).start()

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
