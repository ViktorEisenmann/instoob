# LIMIAR LAB — Instagram API oficial (alternativa ao erro 429)

## Por que esta opção existe

O Instoob original consulta um endpoint privado do Instagram
(`i.instagram.com/api/v1/users/web_profile_info`). Na primeira execução do
LIMIAR LAB em 17/11/2026, o endpoint retornou **HTTP 429** e nenhum Reel foi
identificado. Este fork agora **falha explicitamente** quando essa consulta
não funciona, em vez de reportar um sucesso enganoso.

Como `@vik_limiarlab` é um perfil profissional, podemos consultar os
próprios Reels com a API oficial da Meta, sem uma Página do Facebook.

## Configuração de origem oficial

1. Entre em https://developers.facebook.com/apps/ e crie um app Meta para
   o LIMIAR LAB (tipo Business, quando solicitado).
2. Adicione o produto **Instagram** e selecione **Instagram API with
   Instagram Login** / **API setup with Instagram login**.
3. Na configuração, use a permissão de leitura
   `instagram_business_basic` (não precisamos de acesso a mensagens,
   comentários ou publicação no Instagram).
4. Em **Generate access tokens**, adicione a conta profissional
   `@vik_limiarlab`. Se o painel solicitar um convite de Instagram Tester,
   aceite-o nas configurações da própria conta do Instagram.
5. Clique em **Generate token**, confirme o acesso à conta correta e copie
   o Instagram User Access Token emitido (normalmente prefixado com `IGAA`).
6. Abra https://github.com/ViktorEisenmann/instoob/settings/secrets/actions
   e crie **Repository secret** com:
   - Name: `IG_ACCESS_TOKEN`
   - Secret: o token obtido no dashboard Meta.
7. **Não remova** os três segredos do YouTube. `IG_SESSION_ID` pode
   permanecer salvo, mas o código priorizará `IG_ACCESS_TOKEN` quando existir.
8. Execute **manualmente** o workflow
   https://github.com/ViktorEisenmann/instoob/actions/workflows/sync.yml
   e confira os logs e o upload privado no YouTube Studio.

## Segurança e limites

- Nunca cole o token no chat, README, arquivos versionados ou logs.
- O token precisa pertencer ao próprio `@vik_limiarlab`; o código verifica
  o nome da conta antes de baixar os Reels.
- Um token de longa duração pode expirar após cerca de **60 dias**;
  a renovação do secret ainda **não está automatizada**.
- A API oficial pode omitir `media_url` de conteúdo com músicas protegidas.
  Nesses casos, o download pode falhar e ser necessário usar o arquivo
  original sem trilha licenciada exclusivamente pelo Instagram.
- O estado `data/synced.json` continua evitando duplicatas.
- `SYNC_ENABLED` deve ficar **desativado** até um teste privado aprovado.
- O backend oficial filtra vídeos com permalink `/reel/`, não fotos ou
  publicações comuns. A duração é verificada depois do download, com ffprobe.

## Documentação

- Meta Instagram Platform: https://developers.facebook.com/docs/instagram-platform/
- Instagram API with Instagram Login:
  https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/
- IG Media:
  https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/
