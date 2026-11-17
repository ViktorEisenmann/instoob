"""Offline regression tests for the official Instagram source (no credentials used)."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from src.instagram import InstagramAPIError
from src.instagram_graph import fetch_reels_official


class FakeResponse:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status_code = status
        self.ok = status < 400

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        return self.responses.pop(0)


class InstagramGraphTests(unittest.TestCase):
    def _fetch(self, responses, **overrides):
        options = {
            "username": "vik_limiarlab",
            "max_count": 1,
            "max_duration": 180,
            "already_synced": set(),
            "since_date": datetime(2026, 11, 1, tzinfo=timezone.utc),
            "access_token": "TEST_FAKE_TOKEN",
        }
        options.update(overrides)
        with patch("src.instagram_graph.requests.Session", return_value=FakeSession(responses)):
            return fetch_reels_official(**options)

    def test_only_own_reels_oldest_first_and_no_duplicates(self):
        responses = [
            FakeResponse({"id": "42", "username": "vik_limiarlab"}),
            FakeResponse({"data": [
                {"shortcode": "NEW", "media_type": "VIDEO",
                 "permalink": "https://www.instagram.com/reel/NEW/",
                 "timestamp": "2026-11-16T10:00:00Z", "caption": "Second #Test",
                 "media_url": "https://cdn.example.com/new.mp4"},
                {"shortcode": "OLD", "media_type": "VIDEO",
                 "permalink": "https://www.instagram.com/reel/OLD/",
                 "timestamp": "2026-11-15T10:00:00Z", "caption": "First",
                 "media_url": "https://cdn.example.com/old.mp4"},
                {"shortcode": "PHOTO", "media_type": "IMAGE",
                 "permalink": "https://www.instagram.com/p/PHOTO/",
                 "timestamp": "2026-11-14T10:00:00Z"},
            ]}),
        ]
        reels = self._fetch(responses)
        self.assertEqual([r.shortcode for r in reels], ["OLD"])

    def test_wrong_account_rejected(self):
        with self.assertRaisesRegex(InstagramAPIError, "different account"):
            self._fetch([FakeResponse({"id": "42", "username": "not_the_lab"})])

    def test_graph_api_http_error_exposed(self):
        with self.assertRaisesRegex(InstagramAPIError, "HTTP 429"):
            self._fetch([FakeResponse({}, status=429)])


if __name__ == "__main__":
    unittest.main()
