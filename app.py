from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
from googletrans import Translator
from dotenv import load_dotenv

# Load secrets
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
translator = Translator()

app = Flask(__name__)

# Basic menu data (can be replaced with Google Sheets later)
MENU = {
    "බර්ගර්": "චිකන් බර්ගර් - Rs.750, බීෆ් බර්ගර් - Rs.800, විජි බර්ගර් - Rs.700",
    "බිරියානි": "චිකන් බිරියානි - Rs.950, බීෆ් බිරියානි - Rs.1000",
    "කාලය": "අපි සතියේ සියලු දිනවලම පෙ.ව. 10 සිට රා.8 දක්වා විවෘතව ඇත."
}

@app.route("/bot", methods=["POST"])
def whatsapp_bot():
    user_msg = request.form.get('Body')
    from_number = request.form.get('From')

    translated = translator.translate(user_msg, src='si', dest='en').text.lower()

    if any(item in translated for item in ["menu", "burger", "biryani", "price"]):
        reply = MENU.get("බර්ගර්") + "\n" + MENU.get("බිරියානි")
    elif any(item in translated for item in ["open", "close", "hours", "time"]):
        reply = MENU.get("කාලය")
    else:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful Sinhala-speaking assistant for a restaurant."},
                    {"role": "user", "content": translated}
                ]
            )
            reply = response.choices[0].message.content
        except Exception as e:
            reply = "කණගාටුයි, මට පිළිතුරක් ලබාදිය නොහැක: " + str(e)

    sinhala_reply = translator.translate(reply, src='en', dest='si').text if reply != user_msg else reply

    twiml = MessagingResponse()
    twiml.message(sinhala_reply)
    return str(twiml)

if __name__ == "__main__":
    app.run(debug=True)
