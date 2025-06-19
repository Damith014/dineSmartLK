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

# Sinhala menu and fixed answers
MENU = {
    "බර්ගර්": "🍔 චිකන් බර්ගර් - Rs.750\n🍔 බීෆ් බර්ගර් - Rs.800\n🍔 විජි බර්ගර් - Rs.700",
    "බිරියානි": "🍛 චිකන් බිරියානි - Rs.950\n🍛 බීෆ් බිරියානි - Rs.1000",
    "කාලය": "⏰ අපි සතියේ සියලු දිනවලම පෙරවරු 10 සිට රාත්‍රී 8 දක්වා විවෘතව ඇත."
}

@app.route("/bot", methods=["POST"])
def whatsapp_bot():
    user_msg = request.form.get('Body')
    from_number = request.form.get('From')

    print(f"📩 Incoming from {from_number}: {user_msg}")

    try:
        # Translate Sinhala → English
        translated = translator.translate(user_msg, src='si', dest='en').text.lower()
        print(f"🔤 Translated to English: {translated}")

        # Predefined Sinhala responses
        if any(word in translated for word in ["menu", "burger", "biryani", "rice", "food", "price"]):
            reply = MENU["බර්ගර්"] + "\n\n" + MENU["බිරියානි"]

        elif any(word in translated for word in ["open", "close", "hours", "time"]):
            reply = MENU["කාලය"]

        else:
            # GPT fallback for open questions
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly virtual assistant for a Sri Lankan restaurant. "
                            "Always reply in polite Sinhala. Answer questions about the menu, prices, opening hours, and ordering help."
                        )
                    },
                    {"role": "user", "content": translated}
                ]
            )
            reply = response.choices[0].message.content.strip()

            # Translate GPT reply → Sinhala
            reply = translator.translate(reply, src='en', dest='si').text

        # Fallback in case response is empty
        if len(reply.strip()) < 5:
            reply = "කණගාටුයි, කරුණාකර ඔබගේ ප්‍රශ්නය පැහැදිලිව නැවත යවන්න."

        print(f"✅ Replied: {reply}")
        twiml = MessagingResponse()
        twiml.message(reply)
        return str(twiml)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        twiml = MessagingResponse()
        twiml.message("කණගාටුයි, දෝෂයක් ඇති විය. කරුණාකර පසුව නැවත උත්සාහ කරන්න.")
        return str(twiml)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
