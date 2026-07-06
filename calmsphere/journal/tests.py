from django.test import TestCase
from datetime import date
from .models import Journal


class JournalTest(TestCase):
    def test_journal_creation(self):
        entry = Journal.objects.create(username="testuser", date=date.today(), content="Feeling good today")
        self.assertEqual(entry.username, "testuser")
        self.assertEqual(entry.content, "Feeling good today")

    def test_unique_together(self):
        Journal.objects.create(username="u1", date=date(2025, 1, 1), content="First")
        with self.assertRaises(Exception):
            Journal.objects.create(username="u1", date=date(2025, 1, 1), content="Duplicate")

    def test_journal_retrieval(self):
        Journal.objects.create(username="u1", date=date(2025, 1, 1), content="Day 1")
        Journal.objects.create(username="u1", date=date(2025, 1, 2), content="Day 2")
        entries = Journal.objects.filter(username="u1").order_by("-date")
        self.assertEqual(entries.count(), 2)
        self.assertEqual(entries.first().content, "Day 2")
