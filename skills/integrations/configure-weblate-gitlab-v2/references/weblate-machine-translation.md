# Optional Weblate Machine Translation

## Contents

1. Decision rule
2. No external engine
3. Self-hosted LibreTranslate
4. Third-party providers
5. Configure and verify
6. Failure handling

## 1. Decision rule

Treat machine translation as an optional suggestion source, not as part of the mandatory Weblate–GitLab transport flow.

| Option | Credential | Data location | Typical use |
| --- | --- | --- | --- |
| None | None | Weblate only | BA translates manually or reuses translation memory |
| LibreTranslate self-hosted | None by default | Local Docker deployment | Free proof of concept or data-local requirement |
| Google Cloud Translation Basic | API key | Google Cloud | Simple managed translation |
| Google Cloud Translation Advanced | Service-account JSON | Google Cloud | Glossaries, regions, and managed project controls |
| DeepL | API key | DeepL | Managed translation with DeepL language support |
| Azure AI Translator | API key and region | Microsoft Azure | Organizations already using Azure |
| MyMemory | Optional contact/account credentials | MyMemory | Small non-sensitive experiments only |

Do not install an engine merely because Weblate exposes it. Confirm provider terms, privacy policy, language support, quota, billing, and organizational approval first. Recheck current vendor documentation because these details change.

## 2. No external engine

Leave third-party and self-hosted engines unconfigured when they are unnecessary or not approved. Keep Weblate's built-in exact-match service and Translation Memory enabled when useful.

This mode still supports:

- Manual BA translation.
- PO editing and checks.
- Batch Weblate commits.
- Translation-branch pushes and GitLab MRs.
- CI-generated POT updates, Weblate `msgmerge`, and missing-PO creation when the component file settings permit them.

## 3. Self-hosted LibreTranslate

Run LibreTranslate as a separate container on the same Compose network as Weblate. Do not place it inside the Weblate container.

Example for English and Vietnamese:

```yaml
services:
  libretranslate:
    image: libretranslate/libretranslate:latest
    restart: unless-stopped
    environment:
      LT_UPDATE_MODELS: "true"
      LT_LOAD_ONLY: "en,vi"
    volumes:
      - libretranslate-models:/home/libretranslate/.local:rw

volumes:
  libretranslate-models: {}
```

Merge the example into the existing top-level `services` and `volumes` mappings. Never create a second top-level `services:` or `volumes:` key. Pin a tested image version for a stable deployment.

Start and inspect it:

```bash
docker compose config
docker compose up -d libretranslate
docker compose logs -f libretranslate
```

Wait until both language models are loaded and the server listens on port `5000`. No host port is required when only Weblate calls it over the Compose network.

In Weblate open:

`Administration → Automatic suggestions → LibreTranslate → Install`

Use:

| Field | Value |
| --- | --- |
| Source language selection | Component source language |
| API URL | `http://libretranslate:5000/` |
| API key | Empty unless the self-hosted instance requires one |

LibreTranslate is suitable for draft suggestions and a free proof of concept. Do not assume its output is production-ready for Odoo business terminology.

## 4. Third-party providers

Third-party providers receive content from Weblate. Do not configure one for private repository content until the organization approves that data flow.

### Google Cloud Translation Basic

Use the Weblate service `Google Cloud Translation Basic` for the simplest Google integration.

Prerequisites:

1. Create or select a Google Cloud project.
2. Enable billing and Cloud Translation API.
3. Create an API key.
4. Restrict the key to Cloud Translation API and apply appropriate application restrictions.

In Weblate open:

`Administration → Automatic suggestions → Google Cloud Translation Basic → Install`

Use:

| Field | Value |
| --- | --- |
| Source language selection | Component source language |
| API key | Restricted Google Cloud API key |

Never paste the API key into chat or a committed file.

### Google Cloud Translation Advanced

Use `Google Cloud Translation Advanced` when service-account authentication, glossaries, or region/project controls are required.

Provide:

- Service-account JSON through Weblate's protected configuration form.
- Google Cloud project ID.
- Location closest to or required by the project.
- Cloud Storage bucket only when using glossary files.

Grant only the required Google Cloud roles. Treat the service-account JSON as a secret and rotate it if exposed.

### DeepL

Create a DeepL API subscription and API key. Select the endpoint matching the account:

| Plan | API URL |
| --- | --- |
| API Free | `https://api-free.deepl.com/` |
| API Pro | `https://api.deepl.com/` |

In Weblate install `DeepL`, enter the matching API URL and key, and select component source language. Verify that the required source and target languages are supported by the chosen DeepL plan before saving.

### Azure AI Translator

Create an Azure AI Translator resource and obtain its API key and region. In Weblate install `Azure AI Translator`, then configure:

- API key.
- Region matching the Azure resource.
- Global or regional base URL as required by the resource.
- Custom category only when a custom translator model is actually deployed.

### MyMemory

MyMemory supports anonymous or identified usage but public quotas and IP filtering can make it unreliable for server-side testing. A contact e-mail can increase documented quota but does not guarantee access. If validation returns `403 Forbidden`, do not keep retrying with fake credentials; use a valid account/provider or select another engine.

Do not use MyMemory for sensitive project content without explicit policy approval.

## 5. Configure and verify

For any selected engine:

1. Install it under site-wide or project automatic-suggestion settings.
2. Keep source-language selection tied to the component source language unless the project intentionally uses its secondary language.
3. Save and confirm Weblate's provider validation succeeds.
4. Translate one harmless English test unit into Vietnamese.
5. Verify placeholders, tags, punctuation, plurals, and business terms.
6. Run `Operations → Batch automatic translation` only after the single-unit test succeeds.
7. Review the batch before committing.
8. Deliver approved PO changes through `weblate-translations` and its GitLab MR into `dev`.

Machine translation never creates a GitLab MR by itself. Weblate's repository backend performs commit, push, and MR creation.

## 6. Failure handling

| Symptom | Likely cause | Action |
| --- | --- | --- |
| Provider validation returns `401` or `403` | Invalid key, missing scope, quota, billing, or provider IP policy | Inspect provider console and issue a properly scoped credential |
| LibreTranslate hostname does not resolve | Containers are not on the same Docker network | Attach both services to the same Compose network |
| LibreTranslate connection refused | Container is starting, stopped, or not listening on port `5000` | Inspect `docker compose ps` and service logs |
| Language pair unavailable | Model not loaded or provider does not support the pair | Load the correct model or select another provider |
| Batch output damages placeholders | Engine output was accepted without checks | Stop the batch, review units, and strengthen glossary/check workflow |
| Unexpected provider charges | Batch or suggestion traffic exceeded quota | Disable the provider, inspect usage, set budgets/quotas, and review retry behavior |

Do not confuse provider/API failure with Git synchronization, webhook, or MR failure. Diagnose those paths separately.
