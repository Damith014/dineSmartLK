from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
from googletrans import Translator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
translator = Translator()

app = Flask(__name__)

# Predefined Sinhala menu responses
MENU = {
    "බර්ගර්": "🍔 චිකන් බර්ගර් - Rs.750\n🍔 බීෆ් බර්ගර් - Rs.800\n🍔 විජි බර්ගර් - Rs.700",
    "බිරියානි": "🍛 චිකන් බිරියානි - Rs.950\n🍛 බීෆ් බිරියානි - Rs.1000",
    "කාලය": "⏰ අපි සතියේ සියලු දිනවලම පෙ.ව. 10 සිට රා.8 දක්වා විවෘතව ඇත."
}

@app.route("/bot", methods=["POST"])
def whatsapp_bot():
    user_msg = request.form.get('Body')
    from_number = request.form.get('From')

    print(f"📩 Incoming from {from_number}: {user_msg}")

    try:
        # Translate Sinhala to English for processing
        translated = translator.translate(user_msg, src='si', dest='en').text.lower()
        print(f"🔤 Translated to English: {translated}")

        # Rule-based answers for known questions
        if any(word in translated for word in ["menu", "burger", "biryani", "rice", "food", "price"]):
            reply = MENU["බර්ගර්"] + "\n\n" + MENU["බිරියානි"]
        elif any(word in translated for word in ["open", "close", "hours", "time"]):
            reply = MENU["කාලය"]
        else:
            # Call GPT for anything else
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly restaurant assistant in Sri Lanka who understands English "
                            "and replies politely in Sinhala. Answer questions about the menu, prices, hours, "
                            "and ordering options. Avoid long or overly technical replies."
                        )
                    },
                    {"role": "user", "content": translated}
                ]
            )
            reply = response.choices[0].message.content.strip()

        # Translate GPT's reply back to Sinhala
        sinhala_reply = translator.translate(reply, src='en', dest='si').text

        # Fallback if reply is empty or weird
        if len(sinhala_reply.strip()) < 5:
            sinhala_reply = "කණගාටුයි, කරුණාකර පැහැදිලිව නැවත අයදුම් කරන්න."

        # Return WhatsApp response
        twiml = MessagingResponse()
        twiml.message(sinhala_reply)
        print(f"✅ Replied: {sinhala_reply}")
        return str(twiml)

    except Exception as e:
        error_msg = f"කණගාටුයි, දෝෂයක් සිදුවී ඇත: {str(e)}"
        print(f"❌ ERROR: {error_msg}")
        twiml = MessagingResponse()
        twiml.message(error_msg)
        return str(twiml)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)