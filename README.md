# CalmSphere

CalmSphere is a Django-based mental wellness web app that helps users track moods, write journal entries, receive supportive suggestions, and engage with calming content.

## Project overview

This project contains a Django application with three main apps:

- `core`
  - User authentication and registration
  - Mood tracker with daily logging
  - Personalized dashboard with notifications
  - Monthly mood reports and trends
  - Meditation and wellness content pages
- `journal`
  - Daily journaling with entry history
  - Mood-related journal analytics and streak tracking
- `chatbot`
  - AI companion interface powered by Groq
  - Fallback messaging when API key is not configured

## Key features

- user signup/login with basic validation
- mood tracking with charts and distribution summaries
- dashboard notifications and daily wellness reminders
- monthly mood reporting and journal streak tracking
- journaling with date-based entries
- AI chatbot interface using Groq if available
- built-in meditation, reading, games, and self-help pages

## Requirements

- Python 3.11+ (tested with 3.13)
- Django 6.x
- `groq`
- `python-dotenv`
- `psycopg2-binary`

## Setup

1. Clone the repository:

```bash
git clone https://github.com/Charannoo/clamsphere.git
cd CalmSphere
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the example environment file and configure it:

```bash
copy .env.example .env
```

5. Edit `.env` and add your values:

```text
GROQ_API_KEY=your_groq_api_key_here
DJANGO_SECRET_KEY=generate-a-random-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

6. Run database migrations:

```bash
cd calmsphere
python manage.py migrate
```

7. Create a superuser (optional):

```bash
python manage.py createsuperuser
```

8. Start the development server:

```bash
python manage.py runserver
```

9. Open the app in your browser:

```
http://127.0.0.1:8000/
```

## Running tests

From the `calmsphere` directory:

```bash
python manage.py test
```

## Configuration notes

- The app uses SQLite by default for local development.
- If `GROQ_API_KEY` is not set or invalid, the chatbot falls back to a friendly offline message and the dashboard uses rules-based suggestions.
- `ALLOWED_HOSTS` is loaded from `.env` and defaults to `127.0.0.1,localhost`.

## Project structure

- `calmsphere/` - Django project package
- `core/` - mood tracker, dashboard, auth, notifications
- `journal/` - journal entry handling
- `chatbot/` - AI companion interface
- `static/` - static assets (CSS, JS, images, sound, videos)
- `templates/` - HTML templates for all pages
- `requirements.txt` - Python dependencies
- `.env.example` - sample environment variables

## Notes

- Remove or exclude large media files before pushing to GitHub if you are not using Git LFS.
- The current repository expects a `main` branch on GitHub and uses `master` locally.
