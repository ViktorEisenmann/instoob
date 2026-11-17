"""Main sync orchestrator: Instagram Reels -> YouTube Shorts."""

import logging
import os
import shutil
import subprocess
from pathlib import Path

from .config import AppConfig
from .instagram import (
    download_reel,
    fetch_reels,
)
from .instagram_graph import fetch_reels_official, fetch_reels_unified
from .state import add_synced_reel, get_synced_shortcodes, load_state, save_state
from .youtube import get_authenticated_service, upload_video

logger = logging.getLogger(__name__)


def run_sync(config: AppConfig) -> int:
    """
    Run a full sync cycle. Returns number of reels synced.

    Flow: load state -> fetch reels -> download -> upload -> update state -> cleanup
    """
    username = config.instagram.username
    if not username:
        logger.error("No Instagram username configured")
        return 0

    # Load state
    state = load_state(config.sync.data_dir)
    synced = get_synced_shortcodes(state)
    logger.info(f"Already synced: {len(synced)} reels")

    # Prefer the official, professional-account API when its token is configured.
    official_token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    unified_account_id = os.environ.get("IG_ACCOUNT_ID", "").strip()
    if official_token and unified_account_id:
        logger.info("Using official Meta API with Unified Login")
        reels = fetch_reels_unified(
            username=username,
            max_count=config.instagram.max_reels_per_run,
            max_duration=config.instagram.max_duration,
            already_synced=synced,
            since_date=config.instagram.since_date,
            access_token=official_token,
            account_id=unified_account_id,
        )
    elif official_token:
        logger.info("Using official Instagram API with legacy Instagram Login")
        reels = fetch_reels_official(
            username=username,
            max_count=config.instagram.max_reels_per_run,
            max_duration=config.instagram.max_duration,
            already_synced=synced,
            since_date=config.instagram.since_date,
            access_token=official_token,
        )
    else:
        logger.info("Using legacy unofficial Instagram API (may return HTTP 429)")
        reels = fetch_reels(
            username=username,
            max_count=config.instagram.max_reels_per_run,
            max_duration=config.instagram.max_duration,
            already_synced=synced,
            since_date=config.instagram.since_date,
        )
    logger.info(f"Found {len(reels)} new reels to sync")

    if not reels:
        logger.info("Nothing to sync")
        save_state(config.sync.data_dir, state)
        return 0

    # Set up YouTube
    youtube = get_authenticated_service()

    # Process each reel
    download_dir = Path(config.sync.download_dir)
    download_dir.mkdir(parents=True, exist_ok=True)
    synced_count = 0
    failed_count = 0

    for reel in reels:
        try:
            logger.info(f"Processing reel {reel.shortcode} ({reel.duration}s)")

            # Download
            video_path = download_reel(reel, download_dir)

            # The official media API does not expose duration; check the video after download.
            if config.instagram.max_duration > 0 and reel.duration <= 0:
                try:
                    probe = subprocess.run(
                        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
                        capture_output=True, text=True, check=True, timeout=30,
                    )
                    duration = float(probe.stdout.strip())
                except (FileNotFoundError, subprocess.CalledProcessError, ValueError,
                        subprocess.TimeoutExpired) as exc:
                    raise RuntimeError(
                        "Could not verify downloaded video duration with ffprobe"
                    ) from exc
                if duration > config.instagram.max_duration:
                    logger.info(
                        "Skipping %s: %.1f seconds exceeds %s-second limit",
                        reel.shortcode, duration, config.instagram.max_duration,
                    )
                    video_path.unlink(missing_ok=True)
                    continue

            # Build metadata
            title = _build_title(reel.caption, config.youtube)
            description = _build_description(reel.caption, config.youtube)
            tags = reel.hashtags[:30] if reel.hashtags else []

            # Upload
            yt_id = upload_video(
                youtube=youtube,
                video_path=video_path,
                title=title,
                description=description,
                tags=tags,
                category_id=config.youtube.category_id,
                privacy_status=config.youtube.privacy_status,
                made_for_kids=config.youtube.made_for_kids,
            )

            # Record
            add_synced_reel(state, reel.shortcode, yt_id, title)
            synced_count += 1
            logger.info(f"Synced: {reel.shortcode} -> https://youtube.com/shorts/{yt_id}")

            # Clean up this reel's download
            video_path.unlink(missing_ok=True)

        except Exception:
            failed_count += 1
            logger.exception(f"Failed to sync reel {reel.shortcode}")

    # Save state
    save_state(config.sync.data_dir, state)

    # Clean up downloads dir
    if download_dir.exists():
        shutil.rmtree(download_dir, ignore_errors=True)

    logger.info(f"Sync complete: {synced_count}/{len(reels)} reels synced")
    if failed_count:
        raise RuntimeError(f"Sync failed for {failed_count} Reel(s); inspect logs above")
    return synced_count


def _build_title(caption: str, yt_config) -> str:
    """Build YouTube title from Instagram caption."""
    first_line = caption.split("\n")[0] if caption else "Short"
    # Strip hashtags from title
    title = " ".join(w for w in first_line.split() if not w.startswith("#"))
    title = title.strip() or "Short"
    title = f"{yt_config.title_prefix}{title}{yt_config.title_suffix}"
    return title[:100]


def _build_description(caption: str, yt_config) -> str:
    """Build YouTube description from Instagram caption."""
    desc = caption or ""
    desc += yt_config.description_suffix
    return desc[:5000]
