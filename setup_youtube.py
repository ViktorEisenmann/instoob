"""One-time YouTube OAuth setup for LIMIAR LAB.

Uses both youtube.upload and youtube.readonly so the authorized channel can be
verified *before* the new refresh token is shown or added to GitHub Secrets.

Keep client_secrets.json and the printed tokens local and private.
"""

import json
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
CLIENT_SECRETS_FILE = "client_secrets.json"


def main():
    print("=== LIMIAR LAB - YouTube OAuth Setup ===\n")
    if not Path(CLIENT_SECRETS_FILE).exists():
        print("ERROR: client_secrets.json not found in this directory.")
        print("Download the Desktop OAuth JSON from Google Cloud and rename it.")
        sys.exit(1)

    print("First, select the actual LIMIAR LAB channel in YouTube Studio.")
    print("In Settings > Channel > Advanced settings, copy the Channel ID (UC...).")
    expected_id = input("Paste the intended YouTube Channel ID (UC...): ").strip()
    if not expected_id.startswith("UC") or len(expected_id) < 15:
        print("ERROR: Enter the correct YouTube channel ID, starting with UC.")
        sys.exit(1)

    print("\nOpening the Google consent screen. Choose the LIMIAR LAB channel.")
    print("If Google shows several channels/Brand Accounts, select the correct one.\n")

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(
        port=8080,
        prompt="consent select_account",
        access_type="offline",
    )

    print("\nChecking the authorized YouTube channel...")
    try:
        youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)
        response = youtube.channels().list(part="snippet", mine=True).execute()
    except HttpError as exc:
        print(f"ERROR: Could not inspect the OAuth channel (HTTP {exc.resp.status}).")
        print("Check the consent permissions: upload and view YouTube account.")
        sys.exit(2)

    channels = response.get("items", [])
    if not channels:
        print("ERROR: No YouTube channel returned for this authorization.")
        sys.exit(2)

    for channel in channels:
        title = channel.get("snippet", {}).get("title", "(unnamed)")
        cid = channel.get("id", "(missing)")
        print(f"Authorized channel: {title} | {cid}")

    matching = [ch for ch in channels if ch.get("id") == expected_id]
    if not matching:
        print("\nWRONG CHANNEL! No credentials were printed.")
        print(f"Intended channel ID: {expected_id}")
        print("Run this script again and choose the correct YouTube channel.")
        print("If the picker does not appear, check the default channel in YouTube.")
        sys.exit(3)

    if not credentials.refresh_token:
        print("ERROR: OAuth did not return a refresh token. No credentials printed.")
        print("Revoke this app's access in your Google Account and retry.")
        sys.exit(4)

    with open(CLIENT_SECRETS_FILE, encoding="utf-8") as f:
        client_config = json.load(f)
    installed = client_config.get("installed", client_config.get("web", {}))

    print("\n=== Correct LIMIAR LAB channel confirmed ===")
    print("Save these values ONLY in GitHub Repository Secrets (never in chat):")
    print(f"YOUTUBE_CLIENT_ID={installed['client_id']}")
    print(f"YOUTUBE_CLIENT_SECRET={installed['client_secret']}")
    print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")
    print("\nAdd GitHub Actions Repository variable:")
    print(f"YOUTUBE_EXPECTED_CHANNEL_ID={expected_id}")
    print("\nDo not activate SYNC_ENABLED until the private upload test passes.")


if __name__ == "__main__":
    main()
