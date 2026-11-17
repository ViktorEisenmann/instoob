"""Read-only diagnosis of the YouTube channel authorized by Instoob.

Uses exactly the GitHub repository's YouTube OAuth credentials.
Never prints secrets or access tokens and never uploads, edits or deletes videos.
"""

import sys
from googleapiclient.errors import HttpError
from src.youtube import get_authenticated_service

VIDEO_ID = "uShJDMJb-zc"


def safe_call(request, label):
    try:
        return request.execute()
    except HttpError as exc:
        print(f"{label}: YouTube API returned HTTP {exc.resp.status}.")
        return None
    except Exception as exc:
        print(f"{label}: failed ({type(exc).__name__}); check credentials and scopes.")
        return None


def main():
    print("LIMIAR LAB | Read-only YouTube OAuth/channel diagnosis")
    youtube = get_authenticated_service()

    channels = safe_call(
        youtube.channels().list(part="snippet", mine=True),
        "OAuth channel lookup",
    )
    channel_ids = set()
    if channels is not None:
        items = channels.get("items", [])
        if not items:
            print("OAuth channel lookup returned zero channels.")
        for channel in items:
            cid = channel.get("id", "")
            title = channel.get("snippet", {}).get("title", "(unnamed channel)")
            channel_ids.add(cid)
            print(f"OAuth channel: {title} | ID: {cid}")
            print(f"Channel Studio URL: https://studio.youtube.com/channel/{cid}/videos")

    videos = safe_call(
        youtube.videos().list(part="snippet,status", id=VIDEO_ID),
        "Uploaded video lookup",
    )
    if videos is None:
        print("Cannot confirm video metadata with these OAuth credentials.")
        sys.exit(1)

    items = videos.get("items", [])
    if not items:
        print(f"Video {VIDEO_ID} was NOT returned for these OAuth credentials.")
        print("Possible explanations: different YouTube channel, changed token, or deleted video.")
        sys.exit(2)

    v = items[0]
    snippet = v.get("snippet", {})
    status = v.get("status", {})
    owner_id = snippet.get("channelId", "unknown")
    owner_title = snippet.get("channelTitle", "unknown")
    print(f"Uploaded video: {VIDEO_ID}")
    print(f"Video title: {snippet.get('title', '(no title)')}")
    print(f"Owner channel: {owner_title} | ID: {owner_id}")
    print(f"Privacy: {status.get('privacyStatus', 'unknown')}")
    print(f"Direct Studio editor: https://studio.youtube.com/video/{VIDEO_ID}/edit")
    if channel_ids:
        print(f"Video owner matches OAuth channel: {owner_id in channel_ids}")


if __name__ == "__main__":
    main()
