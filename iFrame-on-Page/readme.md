# Embed an iframe in a Heretto Portal page

**Playbook type:** Implementation — structured content  
**Playbook rank:** 1 — standalone pattern  
**Maturity:** Field-tested  
**Provenance:** Heretto Professional Services; validated against production customer Portal implementations  
**Review status:** Approved for internal reuse; not yet product-reviewed  
**Support boundary:** This is a field-tested implementation pattern. It is not official Heretto product documentation and does not constitute a product support commitment.

---

## What this playbook demonstrates

How to embed an iframe in a Heretto Portal page using DITA. DITA does not have a native `<iframe>` element. Heretto Portal supports iframe rendering through the DITA `<object>` element with `outputclass="iframe"`. The Portal output transform converts that element to a live HTML iframe in the published output.

## Problem it solves

Portal content authors need to embed interactive third-party content—forms, step-by-step tutorials, product demos—directly in documentation pages. Standard DITA documentation and most authoring guides do not cover this capability.

## Validated use cases

| Content type | Source |
|---|---|
| Embedded form | Google Forms |
| Step-by-step tutorial | Scribe |
| Interactive product demo | Navattic |

---

## Package contents

```
iFrame-on-Page/
  README.md                              <- This file
  docs/
    concept.md                           <- Why DITA uses <object> and how Portal renders it
    implementation.md                    <- Step-by-step authoring guide
    troubleshooting.md                   <- Common failures and fixes
    security.md                          <- Security and privacy principles for embedded iframes
  examples/
    dita/
      iframe-example.dita                <- Copy-ready DITA topic with three embed patterns
      iframe-map.ditamap                 <- Sample DITA map for publishing
  design/
    2pager.md                            <- Background: governing informal implementation knowledge
  notes/
    slack-message-iframe-solutoin.txt    <- Original Slack exchange (provenance)
    Embedded_Content.dita                <- Source DITA from validated Portal implementation
    issue-with-sharing-info-this-way.md  <- Governance analysis of informal implementation guidance
```

---

## Quick start

Add this `<object>` element inside any `<section>` or `<body>` in your DITA topic:

```xml
<object
  data="YOUR_EMBED_URL"
  height="600"
  outputclass="iframe">
  <param name="frameborder" value="0"/>
  <param name="width" value="100%"/>
  <param name="allowfullscreen"/>
</object>
```

Replace `YOUR_EMBED_URL` with the embed URL from your third-party content source. Publish to Heretto Portal. The Portal output transform converts the `<object>` element with `outputclass="iframe"` to a live `<iframe>` in the HTML output.

See [docs/implementation.md](docs/implementation.md) for the full authoring guide.

---

## How this maps to Portal publishing

This pattern uses Heretto's DITA publishing pipeline, not the Heretto REST API. The `outputclass="iframe"` attribute is a rendering instruction that Heretto Portal's output transform recognizes. No API credentials or server configuration are required beyond your standard Portal publishing profile.

---

## What to change for production

| Item | What to do |
|---|---|
| Embed URL | Replace example URLs with your content source's embed URL |
| Height | Adjust `height` to fit the content (Google Forms: 600-800; Scribe: 400-600; Navattic: 600-800) |
| Topic placement | Include the topic in your full DITA map hierarchy |
| Publishing profile | Confirm the Portal publishing profile is configured for your environment |

---

## Known limitations

- Validated for **Heretto Portal only**. Behavior in PDF, HTML5, or other output formats is not defined by this pattern.
- The `outputclass="iframe"` rendering rule is specific to Heretto Portal's transform. It is not part of the DITA specification.
- Some third-party sources block embedding via `X-Frame-Options` or `Content-Security-Policy` headers. The iframe element will appear on the page but the embedded content will refuse to load. This is a third-party restriction, not a Heretto limitation.
- Height must be set explicitly. Heretto Portal does not auto-size the iframe to match the embedded content.

---

## Further reading

- [docs/concept.md](docs/concept.md) — Background: why DITA uses `<object>` and how Portal renders it
- [docs/implementation.md](docs/implementation.md) — Full step-by-step authoring guide
- [docs/troubleshooting.md](docs/troubleshooting.md) — Common failures and fixes
- [docs/security.md](docs/security.md) — Security and privacy principles for embedded iframes
- [examples/dita/iframe-example.dita](examples/dita/iframe-example.dita) — Copy-ready DITA examples

---

## Revision history

| Version | Date | Change |
|---|---|---|
| 1.0.0 | 2026-07-24 | Initial playbook package from Slack exchange and validated Portal implementation |
