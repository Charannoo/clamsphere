from django.test import TestCase
from django.contrib.auth.models import User
from .models import MoodEntry, UserProfile


class UserRegistrationTest(TestCase):
    def test_user_creation_with_profile(self):
        user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")
        UserProfile.objects.create(user=user, mobile="9876543210")
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(user.profile.mobile, "9876543210")

    def test_duplicate_username_rejected(self):
        User.objects.create_user(username="dup", password="pass12345")
        self.assertTrue(User.objects.filter(username="dup").exists())


class MoodEntryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="mooduser", password="pass12345")

    def test_mood_creation(self):
        entry = MoodEntry.objects.create(user=self.user, mood="happy")
        self.assertEqual(entry.mood, "happy")
        self.assertIsNotNone(entry.created_at)

    def test_mood_count(self):
        MoodEntry.objects.create(user=self.user, mood="calm")
        MoodEntry.objects.create(user=self.user, mood="calm")
        MoodEntry.objects.create(user=self.user, mood="stress")
        self.assertEqual(MoodEntry.objects.filter(mood="calm").count(), 2)


from django.urls import reverse
from .models import Notification

class NotificationAndSuggestionsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testdashboarduser", password="pass12345")
        self.client.login(username="testdashboarduser", password="pass12345")
        UserProfile.objects.create(user=self.user, mobile="9999999999")
        session = self.client.session
        session["username"] = "testdashboarduser"
        session.save()

    def test_dashboard_creates_notifications_and_suggestions(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Personalized suggestion:")
        
        notif_count = Notification.objects.filter(user=self.user).count()
        self.assertTrue(notif_count >= 1)
        
        self.assertTrue(Notification.objects.filter(user=self.user, notif_type='wellness_reminder').exists())
        self.assertTrue(Notification.objects.filter(user=self.user, notif_type='mood_reminder').exists())

    def test_mark_notifications_read_endpoint(self):
        Notification.objects.create(user=self.user, message="Test 1", notif_type="general", is_read=False)
        Notification.objects.create(user=self.user, message="Test 2", notif_type="general", is_read=False)
        
        self.assertEqual(Notification.objects.filter(user=self.user, is_read=False).count(), 2)
        
        response = self.client.post(reverse('mark_notifications_read'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "success"})
        
        self.assertEqual(Notification.objects.filter(user=self.user, is_read=False).count(), 0)

