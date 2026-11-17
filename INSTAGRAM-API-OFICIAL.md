# LIMIAR LAB — Instagram API oficial via Unified Login (Meta, 2026)

## Estado verificado

A primeira execução do Instoob, em 17/11/2026, encontrou `HTTP 429`
no endpoint privado do Instagram, sem realizar upload.
O fork agora falha corretamente nesses casos e suporta o novo
**Instagram API with Unified Login**, que usa `graph.facebook.com`,
um token **Business Integration System User** e o ID da conta Instagram
atribuída ao portfólio. O código anterior de `graph.instagram.com`
permanece apenas para integrações mais antigas do Instagram Login.

## Passos para a conta @vik_limiarlab

1. No [Meta for Developers](https://developers.facebook.com/apps/),
   abra o aplicativo **LIMIAR LAB Shorts**.
2. Entre em **Use cases → Manage messaging & content on Instagram → Customize →
   API setup with Unified login → 2. Generate access tokens**.
3. Na linha do perfil **@vik_limiarlab**, clique **Generate token** e aceite
   os avisos e permissões necessários para acesso ao seu próprio perfil.
4. **Não compartilhe o token em chat ou arquivos**. Salve-o diretamente como
   **Repository secret** no GitHub com o nome `IG_ACCESS_TOKEN`:
   https://github.com/ViktorEisenmann/instoob/settings/secrets/actions
5. Copie o **Instagram Account ID numérico** exibido na mesma seção.
   Em **Settings → Secrets and variables → Actions → Variables**,
   crie a **Repository variable** `IG_ACCOUNT_ID` com esse número:
   https://github.com/ViktorEisenmann/instoob/settings/variables/actions
6. Deixe os três secrets do YouTube como estão. `IG_SESSION_ID` pode ficar
   armazenado, mas `IG_ACCESS_TOKEN` tem prioridade.
7. Mantenha `SYNC_ENABLED` **ausente ou false**. Faça o primeiro teste
   manual em
   https://github.com/ViktorEisenmann/instoob/actions/workflows/sync.yml
8. Confira logs e o YouTube Studio. Por segurança os uploads permanecem
   **privados** até revisão. Se o teste funcionar, ativar depois a
   variável `SYNC_ENABLED=true` habilita agendamento de seis em seis horas.

## Permissões e testes

- A leitura de perfil e mídias usa a permissão `instagram_basic` em
  **Unified Login**, não `instagram_business_basic`.
- Se o Meta Graph API retornar erro 400 (código 100, subcódigo 33), confirme
  que a conta correta está atribuída ao portfólio. Há relatos de casos em que
  é preciso configurar `business_management` pela interface do
  **Facebook Login for Business** e autorizar novamente; não conceda isso
  preventivamente sem necessidade.
- O token é verificado para garantir que a conta é `@vik_limiarlab` antes
  de listar Reels. Uma conta errada aborta a sincronização.
- A validade do token depende da modalidade emitida pela Meta. Confira
  a expiração na interface/token debugger; **não** assuma 60 dias para Unified Login.
- A API pode omitir `media_url` por direitos autorais. Reels com músicas
  licenciadas no Instagram podem não ser elegíveis para republicação no YouTube.
- O workflow só é considerado funcional de ponta a ponta após um upload
  privado confirmado. Testes unitários não comprovam autorização real.

## Referências

- https://developers.facebook.com/docs/instagram-platform/
- https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/
- https://www.tryadeli.com/blog/instagram-api-unified-login
