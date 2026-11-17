"""Offline safety tests: uploads must target the explicitly approved YouTube channel."""

import unittest
from unittest.mock import MagicMock

from src.youtube import assert_expected_channel


class YouTubeChannelGuardTests(unittest.TestCase):
    def setUp(self):
        self.youtube = MagicMock()
        self.youtube.channels.return_value.list.return_value.execute.return_value = {
            "items": [
                {"id": "UC1111111111111111111111",
                 "snippet": {"title": "Personal Channel"}}
            ]
        }

    def test_missing_expected_channel_blocks_upload(self):
        with self.assertRaisesRegex(RuntimeError, "Upload paused"):
            assert_expected_channel(self.youtube, "")

    def test_wrong_expected_channel_blocks_upload(self):
        with self.assertRaisesRegex(RuntimeError, "Upload blocked"):
            assert_expected_channel(self.youtube, "UC2222222222222222222222")

    def test_matching_expected_channel_is_accepted(self):
        assert_expected_channel(self.youtube, "UC1111111111111111111111")
        self.youtube.channels.return_value.list.assert_called_once_with(
            part="snippet", mine=True
        )


if __name__ == "__main__":
    unittest.main()
