from django.contrib import admin
from django.urls import path
from . import views
from journal.views import journal_view
from chatbot.views import chatbot_page, chatbot_api

handler404 = 'calmsphere.views.custom_404'
handler500 = 'calmsphere.views.custom_500'

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index, name="index"),
    path('login/', views.auth_page, name="login"),
    path('signup/', views.auth_page, name="signup"),
    path('mood/', views.mood_tracker, name="mood"),
    path('save-mood/', views.save_mood, name="save_mood"),
    path('dashboard/', views.dashboard_view, name="dashboard"),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('monthly-report/', views.monthly_report, name='monthly_report'),

    path('logout/', views.logout_view, name="logout"),
    path('journal/', journal_view, name='journal'),
    path('chatbot/', chatbot_page, name='chatbot'),
    path('chatbot/api/', chatbot_api, name='chatbot_api'),
    path('mood-graph/', views.mood_graph, name='mood_graph'),
    path('add-mood/', views.add_mood, name='add_mood'),
    path('selfhelp/', views.self_help, name='selfhelp'),
    path('sound/', views.sound, name='sound'),
    path('reading/', views.reading, name='reading'),
    path('games/', views.games, name='games'),
    path('breathing/', views.breathing, name='breathing'),
    path('book/atomic/', views.book_atomic, name='book_atomic'),
    path('book/power-now/', views.book_power_now, name='book_power_now'),
    path('book/you-can-win/', views.book_you_can_win, name='book_you_can_win'),
    path('book/heal-life/', views.book_heal_life, name='book_heal_life'),
    path('book/overthinking/', views.book_overthinking, name='book_overthinking'),
    path('book/mindfulness/', views.book_mindfulness, name='book_mindfulness'),
    path('games/chess/', views.chess_game, name='chess_game'),
    path('games/sudoku/', views.sudoku_game, name='sudoku_game'),
    path('games/bubble/', views.bubble_game, name='bubble_game'),
    path('games/color/', views.color_game, name='color_game'),
    path('games/memory/', views.memory_game, name='memory_game'),
    path('games/number/', views.number_game, name='number_game'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path("meditation/", views.meditation, name="meditation"),
    path("meditation/breathe/", views.breathe, name="breathe"),
    path("meditation/om/", views.om, name="om"),
    path("meditation/focus/", views.focus, name="focus"),
    path("meditation/bodyscan/", views.bodyscan, name="bodyscan"),
    path("meditation/gratitude/", views.gratitude, name="gratitude"),
    path("meditation/sleep/", views.sleep, name="sleep"),
]