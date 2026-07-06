from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from .models import ChatHistory


class ChatHistoryTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="chatuser", password="pass12345")
        self.client = Client()

    def test_chat_history_created(self):
        ChatHistory.objects.create(
            user=self.user,
            session_key="test-session",
            message="Hello",
            response="Hi there!",
        )
        self.assertEqual(ChatHistory.objects.count(), 1)

    def test_chat_api_requires_post(self):
        response = self.client.get("/chatbot/api/")
        self.assertEqual(response.status_code, 405)

    def test_chat_api_empty_message(self):
        import json
        response = self.client.post(
            "/chatbot/api/",
            data=json.dumps({"message": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_chat_page_loads(self):
        response = self.client.get("/chatbot/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI Companion")
