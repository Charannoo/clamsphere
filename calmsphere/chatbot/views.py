import os
import logging

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from groq import Groq

from .models import ChatHistory

logger = logging.getLogger(__name__)

MENTAL_HEALTH_SYSTEM_PROMPT = (
    "You are CalmSphere AI, a compassionate mental wellness companion. "
    "Respond with empathy, warmth, and evidence-based support. "
    "Keep responses concise (2-4 sentences), calming, and supportive. "
    "If someone expresses crisis or self-harm urges, gently encourage "
    "them to contact a professional helpline (e.g., 988). "
    "You are NOT a replacement for therapy."
)


def _get_groq_client():
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    return Groq(api_key=api_key)


def chatbot_page(request):
    user = request.user if request.user.is_authenticated else None
    history = ChatHistory.objects.filter(
        user=user
    ) if user else ChatHistory.objects.filter(
        session_key=request.session.session_key or ""
    )[:50]
    return render(request, "chatbot.html", {"chat_history": history})


@csrf_exempt
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    import json
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not user_message:
        return JsonResponse({"error": "Message is empty"}, status=400)

    client = _get_groq_client()

    if client is None:
        reply = (
            "I'm currently running in offline mode. "
            "Please set your GROQ_API_KEY in the .env file to activate the AI companion. "
            "For now, try journaling or a breathing exercise to relax."
        )
    else:
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": MENTAL_HEALTH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            reply = completion.choices[0].message.content.strip()
        except Exception as e:
            logger.exception("Groq API call failed")
            reply = "I'm having trouble connecting right now. Please try again later."

    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key or ""

    ChatHistory.objects.create(
        user=user,
        session_key=session_key,
        message=user_message,
        response=reply,
    )

    return JsonResponse({"response": reply})
