from datetime import date, timedelta, datetime

from django.shortcuts import render, redirect
from .models import Journal


def journal_view(request):

    # Render main journal page directly (skip cover page)

    username = request.session.get("username") or (request.user.username if request.user.is_authenticated else None)
    page = int(request.GET.get("page", 1))
    selected_date = request.GET.get("date")

    if request.method == "POST":
        date_value = request.POST.get("date")
        content = request.POST.get("content")
        Journal.objects.update_or_create(
            username=username,
            date=date_value,
            defaults={"content": content}
        )
        return redirect(f"/journal/?page={page}&date={date_value}")

    entry = None
    if selected_date and username:
        # Normalize selected_date to a date object for reliable filtering
        try:
            sel_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
        except Exception:
            sel_date_obj = None
        if sel_date_obj:
            entry = Journal.objects.filter(username=username, date=sel_date_obj).first()

    entries = Journal.objects.filter(username=username).order_by("-date")[:4] if username else []
    total_entries = Journal.objects.filter(username=username).count() if username else 0

    today = date.today()
    monthly_entries = (
        Journal.objects.filter(username=username, date__year=today.year, date__month=today.month).count()
        if username else 0
    )

    longest_streak = 0
    if username:
        dates = list(Journal.objects.filter(username=username).order_by("-date").values_list("date", flat=True))
        current_streak = 0
        previous_date = None
        for entry_date in dates:
            if previous_date is None or previous_date - entry_date == timedelta(days=1):
                current_streak += 1
            else:
                longest_streak = max(longest_streak, current_streak)
                current_streak = 1
            previous_date = entry_date
        longest_streak = max(longest_streak, current_streak)

    average_mood = "Calm"
    if entry and entry.content:
        content_lower = entry.content.lower()
        if any(word in content_lower for word in ["happy", "joy", "grateful", "excited"]):
            average_mood = "Happy"
        elif any(word in content_lower for word in ["sad", "down", "lost", "unhappy"]):
            average_mood = "Sad"
        elif any(word in content_lower for word in ["angry", "frustrated", "upset"]):
            average_mood = "Angry"
        elif any(word in content_lower for word in ["anxious", "worried", "nervous"]):
            average_mood = "Anxious"
        elif any(word in content_lower for word in ["calm", "peace", "relaxed", "balanced"]):
            average_mood = "Calm"

    context = {
        "page_number": page,
        "entry": entry,
        "selected_date": selected_date,
        "entries": entries,
        "total_entries": total_entries,
        "monthly_entries": monthly_entries,
        "longest_streak": longest_streak,
        "average_mood": average_mood,
    }

    return render(request, "journal.html", context)
