from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
from groq import Groq
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now, localdate
from core.models import MoodEntry, UserProfile, Notification
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Count
from datetime import timedelta
from journal.models import Journal

def _get_groq_client():
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or api_key == "your_groq_api_key_here":
        return None
    try:
        return Groq(api_key=api_key)
    except Exception:
        return None

def get_ai_suggestion(user, recent_moods):
    client = _get_groq_client()
    
    # Compile mood descriptions
    mood_list = [entry.get_mood_display() for entry in recent_moods]
    
    if client is not None:
        try:
            if mood_list:
                moods_str = ", ".join(mood_list)
                prompt = f"The user has logged these moods recently: {moods_str}. Provide a brief, supportive, and action-oriented mental wellness recommendation (1-2 sentences) for them today."
            else:
                prompt = "The user has not logged any moods yet. Provide a brief, warm, and inviting welcome message (1-2 sentences) encouraging them to check in and start tracking their well-being."

            system_prompt = (
                "You are CalmSphere AI, a compassionate mental wellness companion. "
                "Respond with empathy, warmth, and supportive, actionable suggestions. "
                "Keep response very concise (maximum 1-2 sentences). "
                "Do not mention any medical or clinical jargon."
            )
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=150,
            )
            return completion.choices[0].message.content.strip()
        except Exception:
            pass
            
    # Fallback to rules-based suggestion
    total_recent = len(recent_moods)
    score_map = {
        'happy': 5, 'excited': 4, 'calm': 3,
        'sad': 2, 'stress': 1, 'angry': 0,
    }
    recent_avg = 0
    if total_recent > 0:
        scores = [score_map.get(m.mood, 0) for m in recent_moods]
        recent_avg = round(sum(scores) / len(scores), 1)

    if total_recent > 0 and recent_avg < 2.5:
        return "Your recent mood trend suggests you could use some extra care. Try the guided breathing exercise or listen to calming sounds."
    elif total_recent > 0 and recent_avg < 4:
        return "You're doing okay. A quick meditation or journaling session could help lift your spirits higher."
    elif total_recent > 0:
        return "Your mood has been positive lately! Consider sharing your strategies with others or trying a new relaxation game."
    else:
        return "Welcome! Start by logging your mood or writing a journal entry to see personalized insights."


# INDEX
def index(request):
    return render(request, 'index.html')

def auth_page(request):

    # REGISTER
    if request.method == "POST" and request.POST.get("action") == "register":

        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        mobile = request.POST.get("mobile", "").strip()

        # Empty field validation
        if not username or not email or not password or not mobile:
            messages.error(request, "All fields are required")
            return redirect("signup")

        # Username validation
        if len(username) < 3:
            messages.error(request, "Username must be at least 3 characters")
            return redirect("signup")

        # Mobile validation
        if not mobile.isdigit() or len(mobile) != 10:
            messages.error(request, "Enter a valid 10-digit mobile number")
            return redirect("signup")

        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address")
            return redirect("signup")

        # Password validation
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return redirect("signup")

        # CHECK EXISTING USERNAME / EMAIL / MOBILE
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already taken")
            return redirect("signup")

        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered")
            return redirect("signup")

        if UserProfile.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered")
            return redirect("signup")

        # CREATE USER
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(user=user, mobile=mobile)

        messages.success(request, "Registration successful")
        return redirect("login")

    # LOGIN
    if request.method == "POST" and request.POST.get("action") == "login":

        username = request.POST.get("username").strip()
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            request.session["username"] = user.username
            return redirect("mood")

        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    show_signup = request.path.endswith('/signup/')
    return render(request, "auth.html", {'show_signup': show_signup})

# MOOD PAGE
@login_required
def mood_tracker(request):

    if request.method == 'POST':
        mood = request.POST.get('mood')

        MoodEntry.objects.create(
            user=request.user,
            mood=mood
        )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'mood': mood})

        return redirect('mood')

    mood_stats = (
        MoodEntry.objects
        .filter(user=request.user)
        .values('mood')
        .annotate(total=Count('mood'))
    )

    mood_counts = {choice[0]: 0 for choice in MoodEntry.MOOD_CHOICES}
    for stat in mood_stats:
        mood_counts[stat['mood']] = stat['total']

    score_map = {
        'happy': 5,
        'excited': 4,
        'calm': 3,
        'sad': 2,
        'stress': 1,
        'angry': 0,
    }

    today = localdate()
    last_week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    recent_entries = MoodEntry.objects.filter(
        user=request.user,
        created_at__date__in=last_week
    ).order_by('created_at')

    week_values = {day: None for day in last_week}
    for entry in recent_entries:
        week_values[entry.created_at.date()] = score_map.get(entry.mood, 0)

    trend_labels = [day.strftime('%a') for day in last_week]
    trend_values = [week_values[day] if week_values[day] is not None else 0 for day in last_week]

    context = {
        'mood_counts': mood_counts,
        'trend_labels_json': json.dumps(trend_labels),
        'trend_values_json': json.dumps(trend_values),
        'mood_stats': mood_stats,
    }

    return render(request, 'mood.html', context)


# SAVE MOOD (AJAX)
@csrf_exempt
def save_mood(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session["mood"] = data.get("mood")
        return JsonResponse({"status": "success"})


# DASHBOARD
@login_required
def dashboard_view(request):
    username = request.session.get("username")
    mood = request.session.get("mood")

    if not username:
        return redirect("login")

    today = localdate()
    recent_moods = MoodEntry.objects.filter(
        user=request.user,
        created_at__date__gte=today - timedelta(days=7)
    ).order_by('-created_at')
    
    total_recent = recent_moods.count()

    score_map = {
        'happy': 5, 'excited': 4, 'calm': 3,
        'sad': 2, 'stress': 1, 'angry': 0,
    }
    recent_avg = 0
    if total_recent > 0:
        scores = [score_map.get(m.mood, 0) for m in recent_moods]
        recent_avg = round(sum(scores) / len(scores), 1)

    # Groq-based Personalized suggestions with local rules fallback
    suggestion = get_ai_suggestion(request.user, recent_moods)

    # Dynamically generate reminders for the current day
    # 1. Mood Check-in Reminder
    mood_today = MoodEntry.objects.filter(user=request.user, created_at__date=today).exists()
    if not mood_today:
        if not Notification.objects.filter(user=request.user, created_at__date=today, notif_type='mood_reminder').exists():
            Notification.objects.create(
                user=request.user,
                notif_type='mood_reminder',
                message="📝 Have you logged your mood today? Small check-ins build big awareness."
            )
    else:
        Notification.objects.filter(user=request.user, created_at__date=today, notif_type='mood_reminder').update(is_read=True)

    # 2. Journaling Reminder
    journal_today = Journal.objects.filter(username=username, date=today).exists()
    if not journal_today:
        if not Notification.objects.filter(user=request.user, created_at__date=today, notif_type='journal_reminder').exists():
            Notification.objects.create(
                user=request.user,
                notif_type='journal_reminder',
                message="📔 Have you written a journal entry today? Reflecting on your day can help calm your mind."
            )
    else:
        Notification.objects.filter(user=request.user, created_at__date=today, notif_type='journal_reminder').update(is_read=True)

    # 3. General daily breathing reminder
    if not Notification.objects.filter(user=request.user, created_at__date=today, notif_type='wellness_reminder').exists():
        Notification.objects.create(
            user=request.user,
            notif_type='wellness_reminder',
            message="🌿 Take a moment to breathe. Try a 2-minute breathing exercise."
        )

    # Retrieve notifications for displaying
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    has_unread = Notification.objects.filter(user=request.user, is_read=False).exists()

    return render(request, 'dashboard.html', {
        "username": username,
        "mood": mood,
        "suggestion": suggestion,
        "recent_avg": recent_avg,
        "total_recent": total_recent,
        "notifications": notifications,
        "has_unread": has_unread,
    })


@csrf_exempt
@login_required
def mark_notifications_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "success"})
    return JsonResponse({"error": "POST required"}, status=405)



@login_required
def monthly_report(request):
    username = request.session.get("username")
    if not username:
        return redirect("login")

    today = localdate()
    first_of_month = today.replace(day=1)

    # Mood entries this month
    monthly_moods = MoodEntry.objects.filter(
        user=request.user,
        created_at__date__gte=first_of_month,
        created_at__date__lte=today
    )
    total_moods = monthly_moods.count()

    # Mood distribution
    mood_distribution = monthly_moods.values('mood').annotate(count=Count('mood')).order_by('-count')
    mood_counts = {choice[0]: 0 for choice in MoodEntry.MOOD_CHOICES}
    for item in mood_distribution:
        mood_counts[item['mood']] = item['count']

    # Most frequent mood
    most_frequent = mood_distribution.first()
    top_mood_code = most_frequent['mood'] if most_frequent else None
    top_mood_label = dict(MoodEntry.MOOD_CHOICES).get(top_mood_code, 'No data')

    # Average mood score (0-5)
    score_map = {
        'happy': 5, 'excited': 4, 'calm': 3,
        'sad': 2, 'stress': 1, 'angry': 0,
    }
    avg_score = 0
    if total_moods > 0:
        total_score = sum(score_map.get(m.mood, 0) for m in monthly_moods)
        avg_score = round(total_score / total_moods, 1)

    # Journal entries this month
    journal_entries_month = Journal.objects.filter(
        username=username,
        date__gte=first_of_month,
        date__lte=today
    ).count()

    # Journal streak (consecutive days this month)
    journal_dates = list(
        Journal.objects.filter(
            username=username, date__gte=first_of_month, date__lte=today
        ).order_by('-date').values_list('date', flat=True)
    )
    current_streak = 0
    if journal_dates:
        check_date = today
        while check_date >= first_of_month:
            if check_date in journal_dates:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break

    # Weekly mood trend
    last_week = [today - timedelta(days=i) for i in range(6, -1, -1)]
    recent_entries = MoodEntry.objects.filter(
        user=request.user,
        created_at__date__in=last_week
    ).order_by('created_at')

    week_values = {day: None for day in last_week}
    for entry in recent_entries:
        week_values[entry.created_at.date()] = score_map.get(entry.mood, 0)

    trend_labels = [day.strftime('%a') for day in last_week]
    trend_values = [week_values[day] if week_values[day] is not None else 0 for day in last_week]

    return render(request, 'monthly_report.html', {
        "username": username,
        "total_moods": total_moods,
        "mood_counts": mood_counts,
        "top_mood": top_mood_label,
        "avg_score": avg_score,
        "journal_entries_month": journal_entries_month,
        "current_streak": current_streak,
        "trend_labels_json": json.dumps(trend_labels),
        "trend_values_json": json.dumps(trend_values),
        "month_name": today.strftime('%B %Y'),
    })


def chatbot_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')

        # Simple reply logic
        reply = "You said: " + user_message

        return JsonResponse({'response': reply})

    return render(request, 'chatbot.html')

@login_required
def mood_graph(request):
    moods = MoodEntry.objects.filter(user=request.user).order_by('created_at')

    dates = [m.created_at.strftime("%d %b") for m in moods]
    values = [m.mood for m in moods]

    return render(request, 'mood_graph.html', {
        'dates': dates,
        'values': values
    })

@login_required
def add_mood(request):
    if request.method == "POST":
        mood = request.POST.get("mood", "").strip()
        valid_moods = [c[0] for c in MoodEntry.MOOD_CHOICES]
        if mood in valid_moods:
            MoodEntry.objects.create(user=request.user, mood=mood)
    return redirect('mood_graph')

@login_required
def self_help(request):
    return render(request, 'selfhelp.html')

@login_required
def sound(request):
    return render(request, 'sound.html')

@login_required
def reading(request):
    return render(request, 'reading.html')

@login_required
def games(request):
    return render(request, 'games.html')

@login_required
def breathing(request):
    return render(request, 'breathing.html')

@login_required
def book_atomic(request):
    pages = [
        "Have you ever tried to completely change your life overnight… and failed? The problem isn’t your goal — it’s how you approach change.",

        "This book reveals a powerful truth: small habits, repeated daily, create massive transformation over time. Tiny actions matter more than big intentions.",

        "Most people focus only on results, but real success comes from building strong daily systems. What you do every day shapes who you become.",

        "Your environment silently influences your behavior. When you design it right, good habits become easy and natural.",

        "Now imagine improving just 1% every day… In a year, your life could be completely different. This book shows how that transformation really works."
    ]
    return render(request, 'books/reader.html', {'title': 'Atomic Habits', 'pages': json.dumps(pages)})

@login_required
def book_power_now(request):
    pages = [
        "Do you often feel stressed thinking about the past or worried about the future? You’re not alone — most people live this way.",

        "This book teaches a simple but powerful truth: peace exists only in the present moment, not in what has already happened or what might happen.",

        "Your mind constantly pulls you away from the present, creating unnecessary stress and anxiety.",

        "But what if you could learn to stay calm and fully aware of the now, no matter what’s happening around you?",

        "This book opens the door to a deeper sense of peace — something far beyond temporary relaxation."
    ]
    return render(request, 'books/reader.html', {'title': 'The Power of Now', 'pages': json.dumps(pages)})

@login_required
def book_you_can_win(request):
    pages = [
        "Have you ever felt like success is meant for others, not for you? That belief alone can hold you back more than anything else.",

        "This book shows that success begins with your mindset. The way you think directly shapes your future.",

        "Confidence, discipline, and positive thinking are not talents — they are skills you can develop.",

        "Your attitude determines how you handle challenges, failures, and opportunities in life.",

        "What if you could train your mind to think like a winner? This book shows you how to build that mindset step by step."
    ]
    return render(request, 'books/reader.html', {'title': 'You Can Win', 'pages': json.dumps(pages)})

@login_required
def book_heal_life(request):
    pages = [
        "Have you ever noticed how your thoughts affect your mood and your life? What if they affect even more than you realize?",

        "This book teaches that your thoughts and beliefs shape your reality — including your health, happiness, and relationships.",

        "Negative patterns often come from deep-rooted beliefs we are not even aware of.",

        "By changing the way you think, you can begin to heal emotionally and mentally.",

        "This book guides you toward self-love and inner healing — something that can transform your entire life."
    ]
    return render(request, 'books/reader.html', {'title': 'You Can Heal Your Life', 'pages': json.dumps(pages)})

@login_required
def book_overthinking(request):
    pages = [
        "Do your thoughts keep running even when you want to relax? Overthinking can quietly drain your energy and peace.",

        "This book explains why the mind gets stuck in endless loops of worry and analysis.",

        "Most thoughts are not as important as they seem, yet we give them too much power.",

        "Learning to step back and observe your thoughts can reduce stress and bring clarity.",

        "What if you could calm your mind and feel lighter every day? This book shows practical ways to break free from overthinking."
    ]
    return render(request, 'books/reader.html', {'title': 'Overthinking Cure', 'pages': json.dumps(pages)})

@login_required
def book_mindfulness(request):
    pages = [
        "Have you ever tried to sit quietly but found your mind wandering everywhere? That’s completely normal.",

        "This book explains mindfulness in a simple way — being fully aware of the present moment without judgment.",

        "Instead of fighting your thoughts, you learn to observe them calmly and let them pass.",

        "Even a few minutes of mindfulness can reduce stress and improve focus.",

        "This book gently guides you into meditation and awareness — helping you experience true mental clarity."
    ]
    return render(request, 'books/reader.html', {'title': 'Mindfulness in Plain English', 'pages': json.dumps(pages)})

# INDIVIDUAL GAMES
@login_required
def chess_game(request):
    return render(request, 'chess.html')
 
@login_required
def sudoku_game(request):
    return render(request, 'sudoku.html')
 
@login_required
def bubble_game(request):
    return render(request, 'bubble.html')
 
@login_required
def color_game(request):
    return render(request, 'color_therapy.html')
 
@login_required
def memory_game(request):
    return render(request, 'memory.html')
 
@login_required
def number_game(request):
    return render(request, 'number.html')

@login_required
def meditation(request):
    return render(request, "meditation.html")

@login_required
def breathe(request):
    return render(request, "breathe.html")

@login_required
def om(request):
    return render(request, "om.html")

@login_required
def focus(request):
    return render(request, "focus.html")

@login_required
def bodyscan(request):
    return render(request, "bodyscan.html")

@login_required
def gratitude(request):
    return render(request, "gratitude.html")

@login_required
def sleep(request):
    return render(request, "sleep.html")

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

def custom_500(request, exception=None):
    return render(request, '500.html', status=500)

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def admin_users(request):
    try:
        if not request.user.profile.is_admin:
            return redirect("mood")
    except UserProfile.DoesNotExist:
        return redirect("mood")

    users = User.objects.all().select_related('profile')
    return render(request, 'admin_users.html', {'users': users})