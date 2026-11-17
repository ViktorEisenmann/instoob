"""Offline regression tests for the official Instagram source (no credentials used)."""

import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from src.instagram import InstagramAPIError
from src.instagram_graph import fetch_reels_official, fetch_reels_unified


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



class InstagramUnifiedTests(unittest.TestCase):
    def _fetch(self, responses, **overrides):
        options = {
            "username": "vik_limiarlab",
            "max_count": 1,
            "max_duration": 180,
            "already_synced": set(),
            "since_date": datetime(2026, 11, 1, tzinfo=timezone.utc),
            "access_token": "TEST_FAKE_UNIFIED_TOKEN",
            "account_id": "123456789",
        }
        options.update(overrides)
        fake = FakeSession(responses)
        with patch("src.instagram_graph.requests.Session", return_value=fake):
            output = fetch_reels_unified(**options)
        return output

    def test_unified_login_fetches_reel_and_skips_photo(self):
        responses = [
            FakeResponse({"id": "123456789", "username": "vik_limiarlab"}),
            FakeResponse({"data": [
                {"shortcode": "NEW", "media_type": "VIDEO", "media_product_type": "REELS",
                 "permalink": "https://www.instagram.com/reel/NEW/",
                 "timestamp": "2026-11-16T10:00:00Z", "caption": "New reel #LimiarLab",
                 "media_url": "https://cdn.example.com/reel.mp4"},
                {"shortcode": "IMG", "media_type": "IMAGE", "media_product_type": "FEED",
                 "permalink": "https://www.instagram.com/p/IMG/",
                 "timestamp": "2026-11-16T11:00:00Z"},
            ]}),
        ]
        reels = self._fetch(responses)
        self.assertEqual([r.shortcode for r in reels], ["NEW"])
        self.assertEqual(reels[0].hashtags, ["LimiarLab"])

    def test_unified_login_rejects_wrong_username(self):
        with self.assertRaisesRegex(InstagramAPIError, "does not resolve"):
            self._fetch([FakeResponse({"id": "123456789", "username": "someone_else"})])

    def test_unified_login_rejects_non_numeric_account_id(self):
        with self.assertRaisesRegex(InstagramAPIError, "numeric"):
            self._fetch([], account_id="not-an-id")

    def test_unified_login_api_failure_is_not_reported_as_zero_reels(self):
        with self.assertRaisesRegex(InstagramAPIError, "HTTP 400"):
            self._fetch([FakeResponse({}, status=400)])


if __name__ == "__main__":
    unittest.main()
