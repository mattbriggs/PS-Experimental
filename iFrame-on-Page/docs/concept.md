# Embedded iframes in Heretto Portal: concept

## Why DITA does not have an iframe element

DITA is a structured content standard designed to produce output across multiple formats: HTML, PDF, DITA-OT transforms, and proprietary publishing systems. The HTML `<iframe>` element is browser-specific and has no meaning in PDF or other non-browser outputs.

DITA addresses this through the `<object>` element, which is the DITA equivalent of the HTML `<object>` or `<embed>` element. The `<object>` element accepts arbitrary `data`, `height`, and `width` attributes, plus child `<param>` elements for additional rendering instructions. This makes it flexible enough to represent embedded browser content without hard-coding browser-specific markup into the content model.

## How Heretto Portal renders the object element

Heretto Portal's output transform includes a rendering rule that converts a DITA `<object>` element with `outputclass="iframe"` to an HTML `<iframe>` in the published output. The `data` attribute value becomes the `src` of the iframe. The `<param>` child elements map to iframe attributes.

The key requirement is the `outputclass="iframe"` attribute. Without it, the `<object>` element is rendered as an HTML `<object>` element, not an iframe. The embedded content may still appear, but browser handling of `<object>` for external URLs is inconsistent and unreliable.

### Attribute mapping

| DITA attribute or element | HTML iframe output |
|---|---|
| `<object data="URL">` | `<iframe src="URL">` |
| `height="N"` | `height="N"` |
| `outputclass="iframe"` | Triggers iframe rendering (removed from output) |
| `<param name="frameborder" value="0"/>` | `frameborder="0"` |
| `<param name="width" value="100%"/>` | `width="100%"` |
| `<param name="allowfullscreen"/>` | `allowfullscreen` |

## When to use embedded iframes

Use an embedded iframe when:

- The third-party tool provides an embed URL designed for iframe use (Google Forms, Scribe, Navattic, Loom, YouTube, and similar tools all publish embed URLs).
- The embedded content must remain interactive (forms that submit, tutorials that track progress, demos that respond to user input).
- The content changes frequently and should be maintained in the source tool rather than reproduced in DITA.

Do not use an embedded iframe when:

- The content is static and can be described with text and images in DITA directly.
- The third-party source does not provide an embed URL.
- The content must print correctly in PDF output.
- You cannot confirm the third-party source allows embedding from your Portal domain.

## Security and third-party content

Heretto Portal does not control what an embedded iframe loads. Before embedding content from a third-party source, confirm:

- The source URL is from a trusted domain.
- The content does not collect sensitive user data without disclosure.
- The third-party tool's terms of service permit embedding in your documentation portal.
- The source URL is the embed-specific URL, not the page URL. Most tools provide a separate embed or share URL.

Some third-party sources set `X-Frame-Options: DENY` or `X-Frame-Options: SAMEORIGIN` headers, or use `Content-Security-Policy: frame-ancestors` directives that prevent embedding outside their own domain. If a source blocks embedding, the iframe will render on the page but the content will show a blank area or a browser error. This cannot be worked around from the DITA authoring side.
