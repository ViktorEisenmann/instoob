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

## Diagnóstico de canal YouTube (17/11/2026)

O upload de teste retornou `uShJDMJb-zc`, mas o vídeo não apareceu no
YouTube Studio do canal que o usuário estava consultando. Isso pode indicar
que as credenciais OAuth autorizam **outro canal/Brand Account**.

- Abra o workflow manual, **somente leitura**:
  https://github.com/ViktorEisenmann/instoob/actions/workflows/diagnose-youtube.yml
- Clique em **Run workflow** (branch `main`).
- Nos logs de **Read YouTube channel and uploaded video metadata**, confira:
  `OAuth channel`, `Owner channel`, `Privacy`, e `Channel Studio URL`.
- O diagnóstico não publica nem altera vídeos.
- Para futuros uploads, o sync foi protegido por
  **Actions variable** `YOUTUBE_EXPECTED_CHANNEL_ID`: sem o ID de canal
  `UC...` verificado, **nenhum novo vídeo é enviado**.
- Se o canal autorizado não é o LIMIAR LAB, rode novamente
  `setup_youtube.py` escolhendo explicitamente o canal certo no
  seletor do Google/YouTube, atualize o `YOUTUBE_REFRESH_TOKEN` como
  Repository secret e repita o diagnóstico.
- Deixe `SYNC_ENABLED` como `false` ou ausente enquanto o destino
  estiver em investigação.

## Canal de destino correto (17/11/2026)

O primeiro upload `uShJDMJb-zc` foi enviado a um **canal diferente** do
LIMIAR LAB. O usuário confirmou o problema no YouTube. O registro do Reel
`DfmSAZtIfk0` foi removido de `data/synced.json` para permitir novo upload
no canal correto, mas nenhum novo upload foi executado.

**Procedimento no Windows:**

1. No YouTube, selecione o canal LIMIAR LAB, depois abra
   https://www.youtube.com/account_advanced e copie o ID de canal que começa por `UC`.
2. Baixe a versão mais recente do fork (não use a pasta antiga sem atualização):
   https://github.com/ViktorEisenmann/instoob/archive/refs/heads/main.zip
3. Copie seu `client_secrets.json` privado para a pasta `instoob-main`.
4. Abra o PowerShell nessa pasta e execute:

   ```powershell
   py -m venv .venv
   .\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
   .\\.venv\\Scripts\\python.exe setup_youtube.py
   ```

5. Cole o ID do **canal LIMIAR LAB** no terminal.
6. Ao abrir o Google, selecione o canal LIMIAR LAB no seletor da conta/canal.
   A nova autorização solicita `youtube.upload` e `youtube.readonly`,
   pois precisa conferir o canal antes do upload.
7. O programa interrompe com segurança se o ID do canal autenticado for
   diferente. Só se corresponder ele mostra `YOUTUBE_REFRESH_TOKEN`.
8. Atualize **Repository secret** `YOUTUBE_REFRESH_TOKEN` no GitHub.
   Se o cliente Google Cloud for o mesmo, `YOUTUBE_CLIENT_ID` e
   `YOUTUBE_CLIENT_SECRET` não precisam mudar.
9. Crie **Repository variable** `YOUTUBE_EXPECTED_CHANNEL_ID` com o ID
   correto. Não confunda com `IG_ACCOUNT_ID`.
10. Mantenha `SYNC_ENABLED` ausente ou `false` e execute o sync
    manualmente. Confira o novo Short privado no Studio do LIMIAR LAB.
11. Depois, remova manualmente o vídeo privado do canal incorreto, se desejar.

Se o Google não apresentar o canal correto na seleção, consulte as
instruções oficiais para configurar o canal padrão quando aplicativos de
terceiros não oferecem o seletor:
https://support.google.com/youtube/answer/3046478

**Segurança:** nunca envie o JSON, a senha nem os tokens na conversa;
não suba `client_secrets.json` ao GitHub. Somente o ID público do canal
pode ser compartilhado normalmente.
