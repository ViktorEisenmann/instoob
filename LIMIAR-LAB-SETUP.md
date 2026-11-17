# LIMIAR LAB · Instoob

**Status 17/11/2026:** first manual workflow completed but the unofficial Instagram endpoint returned HTTP 429 and uploaded zero Reels. The fork now reports that error correctly and has an optional official Instagram API integration. To activate it, see [INSTAGRAM-API-OFICIAL.md](./INSTAGRAM-API-OFICIAL.md).

Fork of [sunithvs/instoob](https://github.com/sunithvs/instoob) to mirror Reels from [@vik_limiarlab](https://www.instagram.com/vik_limiarlab/) to YouTube Shorts.

## Safety defaults
- Uploads are **private** until reviewed (see `config.yml`).
- At most **one** Reel per run, maximum **180 seconds**.
- Only Reels dated **2026-11-01** or later are eligible.
- The scheduled workflow runs every 6 hours **only when** the repository Actions variable `SYNC_ENABLED` equals `true`. It is intentionally not set by this setup.
- History in `data/synced.json` was reset to remove upstream sample videos.
- **Caution:** Instagram access uses an unofficial private endpoint and a sensitive session cookie. It may break or prompt a security challenge. Never commit cookies or OAuth tokens.
- **Caution:** music licensed inside Instagram is not necessarily licensed for YouTube.

## Finish setup

1. Create a Google Cloud project and enable **YouTube Data API v3**.
2. Configure an OAuth consent screen and create a **Desktop app** OAuth client.
3. Download the client JSON **locally** as `client_secrets.json` (never commit it).
4. Run `pip install -r requirements.txt` then `python setup_youtube.py` locally and sign into the Google account for the correct YouTube channel.
5. Add these repository **Actions secrets** at [Settings](https://github.com/ViktorEisenmann/instoob/settings/secrets/actions): `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, and `YOUTUBE_REFRESH_TOKEN`.
6. **Recommended: Meta Unified Login (2026).** Follow [INSTAGRAM-API-OFICIAL.md](./INSTAGRAM-API-OFICIAL.md), add `IG_ACCESS_TOKEN` as a Repository secret and `IG_ACCOUNT_ID` as a Repository variable. The existing `IG_SESSION_ID` is a legacy fallback; the unofficial endpoint returned HTTP 429 during the first test. Do not share either credential in chat or logs.
7. In **Actions → LIMIAR LAB - Reels to Shorts → Run workflow**, trigger the **manual** test. This does **not** require `SYNC_ENABLED`; the YouTube upload stays private.
8. Verify in YouTube Studio that the video is private and metadata is correct. Check GitHub Actions logs if there is no upload.
9. **Only after the private test passes**, create repository Actions **variable** `SYNC_ENABLED` with value `true` under **Settings → Secrets and variables → Actions → Variables**. This activates scheduled private uploads every six hours. To pause automatic sync, change it to `false`.
10. Change `youtube.privacy_status` to `public` later only if you explicitly want public auto-posting.

**OAuth warning:** Google OAuth apps in External/Testing mode may issue refresh tokens that expire after seven days. Confirm the consent-screen publishing status and any verification requirements.

**Note:** This is a fork of an independent open-source tool, not an official Meta integration. Scheduled GitHub Actions jobs can run late or occasionally be skipped.

## Source
The original project README contains general setup and troubleshooting: https://github.com/sunithvs/instoob
