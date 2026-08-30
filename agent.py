from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

while True:
    question = input("Դու: ")

    if question.lower() == "exit":
        print("AI: Ցտեսություն 👋")
        break

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=question
    )

    print("AI:", response.text)
