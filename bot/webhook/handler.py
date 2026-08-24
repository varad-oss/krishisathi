"""
WhatsApp Bot Webhook Handler for KrishiSathi
Uses Twilio WhatsApp Sandbox for the hackathon prototype.

Setup:
1. Go to https://www.twilio.com/console/sms/whatsapp/sandbox
2. Set webhook URL to: https://YOUR-CLOUD-RUN-URL/bot/webhook
3. Send "join <sandbox-code>" to the Twilio WhatsApp number

This handler processes incoming WhatsApp messages and routes them to the
appropriate KrishiSathi API endpoint.
"""

import os
import base64
import httpx
from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse

router = APIRouter(prefix="/bot", tags=["WhatsApp Bot"])

# KrishiSathi API base URL (same server)
API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api")

# Default location (Pune, India) when no location is shared
DEFAULT_LAT = 18.5204
DEFAULT_LNG = 73.8567


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages from Twilio."""
    form_data = await request.form()
    
    incoming_msg = form_data.get("Body", "").strip()
    num_media = int(form_data.get("NumMedia", 0))
    sender = form_data.get("From", "")
    
    resp = MessagingResponse()
    msg = resp.message()
    
    # If the user sent an image -> crop disease diagnosis
    if num_media > 0:
        media_url = form_data.get("MediaUrl0", "")
        media_type = form_data.get("MediaContentType0", "image/jpeg")
        
        # Download the image
        async with httpx.AsyncClient() as client:
            image_response = await client.get(media_url)
            image_bytes = image_response.content
        
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # Determine crop type from message text (if any)
        crop_type = incoming_msg if incoming_msg else None
        
        # Call diagnosis API
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                diagnosis_resp = await client.post(
                    f"{API_BASE}/diagnose/base64",
                    json={
                        "image": image_b64,
                        "crop_type": crop_type,
                        "latitude": DEFAULT_LAT,
                        "longitude": DEFAULT_LNG,
                        "language": "en",
                    },
                )
                
                if diagnosis_resp.status_code == 200:
                    data = diagnosis_resp.json()
                    
                    response_text = (
                        f"🔬 *Crop Disease Diagnosis*\n\n"
                        f"🦠 *Disease:* {data.get('disease_name', 'Unknown')}\n"
                        f"📊 *Confidence:* {float(data.get('confidence', 0)) * 100:.0f}%\n"
                        f"⚠️ *Severity:* {data.get('severity', 'Unknown')}\n"
                        f"🌿 *Affected:* {data.get('affected_part', 'Unknown')}\n\n"
                    )
                    
                    treatment = data.get("treatment", {})
                    if treatment.get("immediate"):
                        response_text += "💊 *Immediate Actions:*\n"
                        for step in treatment["immediate"][:3]:
                            response_text += f"  • {step}\n"
                    
                    if treatment.get("organic"):
                        response_text += "\n🌱 *Organic Treatment:*\n"
                        for step in treatment["organic"][:2]:
                            response_text += f"  • {step}\n"
                    
                    if treatment.get("chemical"):
                        response_text += "\n🧪 *Chemical Treatment:*\n"
                        for step in treatment["chemical"][:2]:
                            response_text += f"  • {step}\n"
                    
                    response_text += "\n📝 Reply with any question for more advice!"
                    msg.body(response_text)
                else:
                    msg.body(
                        "❌ Sorry, I couldn't analyze that image right now. "
                        "Please try again or send a clearer photo of the affected crop."
                    )
            except Exception as e:
                msg.body(
                    "⏳ The AI is taking longer than usual. "
                    "Please try again in a moment."
                )
    
    # Text message -> advisory chat
    elif incoming_msg:
        # Handle special commands
        lower_msg = incoming_msg.lower()
        
        if lower_msg in ["hi", "hello", "hey", "start", "help"]:
            msg.body(
                "🌾 *Welcome to KrishiSathi!* 🤖\n\n"
                "I'm your AI farming companion. Here's what I can do:\n\n"
                "📸 *Send a photo* of your crop → I'll diagnose any disease\n"
                "💬 *Ask a question* → I'll give farming advice\n\n"
                "Try these:\n"
                "• 'How to manage wheat rust?'\n"
                "• 'Best time to plant rice?'\n"
                "• 'Organic pest control for cotton'\n"
                "• 'Weather forecast for farming'\n\n"
                "🌍 Available in Hindi, Marathi, Tamil, Telugu, Bengali, Kannada, Gujarati, Punjabi, and Malayalam!\n\n"
                "Send your query in any language. 🗣️"
            )
        elif lower_msg == "weather":
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    weather_resp = await client.get(
                        f"{API_BASE}/weather",
                        params={"lat": DEFAULT_LAT, "lng": DEFAULT_LNG},
                    )
                    if weather_resp.status_code == 200:
                        w = weather_resp.json()
                        msg.body(
                            f"🌤️ *Weather Update*\n\n"
                            f"📍 Location: {w.get('location', 'Your area')}\n"
                            f"🌡️ Temperature: {w.get('temp', 'N/A')}°C\n"
                            f"💧 Humidity: {w.get('humidity', 'N/A')}%\n"
                            f"🌧️ Rainfall: {w.get('rainfall', 0)}mm\n"
                            f"💨 Wind: {w.get('wind', 'N/A')} km/h\n"
                            f"📝 {w.get('description', '')}"
                        )
                    else:
                        msg.body("Unable to fetch weather data right now.")
                except Exception:
                    msg.body("Weather service is temporarily unavailable.")
        else:
            # General advisory query
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    advisory_resp = await client.post(
                        f"{API_BASE}/advisory",
                        json={
                            "query": incoming_msg,
                            "latitude": DEFAULT_LAT,
                            "longitude": DEFAULT_LNG,
                            "language": "en",
                        },
                    )
                    
                    if advisory_resp.status_code == 200:
                        data = advisory_resp.json()
                        advisory_text = data.get("advisory_text", "")
                        # Truncate if too long for WhatsApp (1600 char limit)
                        if len(advisory_text) > 1500:
                            advisory_text = advisory_text[:1500] + "..."
                        
                        msg.body(f"🌾 *KrishiSathi Advisory*\n\n{advisory_text}")
                    else:
                        msg.body(
                            "I'm having trouble processing your query. "
                            "Please try rephrasing or ask a simpler question."
                        )
                except Exception:
                    msg.body(
                        "⏳ The AI is taking longer than usual. "
                        "Please try again in a moment."
                    )
    else:
        msg.body(
            "🌾 Welcome to KrishiSathi!\n"
            "Send a photo of your crop or ask a farming question to get started."
        )
    
    return Response(content=str(resp), media_type="application/xml")
