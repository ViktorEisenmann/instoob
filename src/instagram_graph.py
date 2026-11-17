"""Optional official Instagram API with Instagram Login media discovery.

When IG_ACCESS_TOKEN is set, the Instoob fork reads the account's own Reels
through Meta's supported graph.instagram.com API instead of the unofficial
web_profile_info endpoint. The YouTube upload pipeline remains unchanged.

Required permission: instagram_business_basic.
Only use a token obtained for the same professional Instagram account as
config.instagram.username.
"""

import logging
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from .instagram import ReelInfo, InstagramAPIError

logger = logging.getLogger(__name__)
GRAPH_API = "https://graph.instagram.com/v27.0"


def _get_json(session: requests.Session, url: str, params: dict | None = None) -> dict:
    """Issue an authenticated Graph API request without leaking access tokens in errors."""
    try:
        response = session.get(url, params=params, timeout=25)
    except requests.exceptions.RequestException:
        raise InstagramAPIError(
            "Cannot reach the official Instagram Graph API (network error)."
        ) from None
    if not response.ok:
        status = response.status_code
        raise InstagramAPIError(
            f"Official Instagram API returned HTTP {status}. "
            "Check the access token, its expiration, and instagram_business_basic permission."
        ) from None
    try:
        data = response.json()
    except ValueError:
        raise InstagramAPIError("Official Instagram API returned invalid JSON.") from None
    if not isinstance(data, dict) or data.get("error"):
        raise InstagramAPIError("Official Instagram API returned an error response.")
    return data


def fetch_reels_official(
    username: str,
    max_count: int,
    max_duration: int,
    already_synced: set[str],
    since_date: datetime | None,
    access_token: str,
) -> list[ReelInfo]:
    """List owned Reels using the official Instagram API with Instagram Login.

    The API does not provide video duration in the media list, so the duration
    field is left at 0 and validated against the downloaded file by sync.py.
    """
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "LIMIAR-LAB-Instoob/1.0",
    })

    profile = _get_json(session, f"{GRAPH_API}/me", {"fields": "id,username"})
    actual_username = str(profile.get("username", "")).lower().lstrip("@")
    if actual_username != username.lower().lstrip("@"):
        raise InstagramAPIError(
            "The Instagram API token belongs to a different account. "
            "Check which professional Instagram profile you authorized."
        )

    results: list[ReelInfo] = []
    url = f"{GRAPH_API}/me/media"
    params = {
        "fields": "id,caption,media_type,media_url,permalink,timestamp,shortcode",
        "limit": 50,
    }
    pages = 0
    while url and pages < 5:
        data = _get_json(session, url, params)
        pages += 1
        old_page_reached = False

        for item in data.get("data", []):
            permalink = str(item.get("permalink") or "")
            if item.get("media_type") != "VIDEO" or "/reel/" not in permalink.lower():
                continue

            try:
                posted = datetime.fromisoformat(str(item["timestamp"]).replace("Z", "+00:00"))
                if posted.tzinfo is None:
                    posted = posted.replace(tzinfo=timezone.utc)
            except (KeyError, ValueError, TypeError):
                logger.warning("Skipping media with missing/invalid timestamp")
                continue
            if since_date and posted < since_date:
                old_page_reached = True
                continue

            shortcode = str(item.get("shortcode") or "")
            if not shortcode:
                parts = [p for p in urlparse(permalink).path.split("/") if p]
                if len(parts) >= 2 and parts[0].lower() == "reel":
                    shortcode = parts[1]
            if not shortcode or shortcode in already_synced:
                continue

            caption = str(item.get("caption") or "")
            video_url = str(item.get("media_url") or "")
            # Meta can omit media_url for copyrighted music.
            if not video_url:
                logger.warning(
                    "Reel %s has no media_url (possible music rights limitation); "
                    "downloader may need a compatible original file", shortcode
                )
            hashtags = [w.lstrip("#").strip(".,!?") for w in caption.split() if w.startswith("#")]
            results.append(ReelInfo(
                shortcode=shortcode,
                caption=caption,
                hashtags=hashtags,
                video_url=video_url,
                duration=0.0,
                date=posted,
            ))

        if old_page_reached:
            break
        url = data.get("paging", {}).get("next")
        params = None  # Next page URL includes its own cursor; authorization stays in the header.

    results.sort(key=lambda reel: reel.date)
    logger.info(
        "Official Instagram API found %s eligible Reels for @%s",
        len(results),
        username,
    )
    return results[:max_count]
