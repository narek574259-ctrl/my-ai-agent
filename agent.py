import os
from flask import Flask, request, jsonify
from google import genai

app = Flask(__name__)

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)

@app.route("/", methods=["GET"])
def home():
    return "AI Agent is running! 🤖"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=question
    )

    return jsonify({
        "answer": response.text
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
