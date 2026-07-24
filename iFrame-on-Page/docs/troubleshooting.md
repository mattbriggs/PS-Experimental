# Embedded iframe troubleshooting

## Iframe does not appear on the Portal page

### Symptom

The page renders but there is no iframe in the expected location.

### Likely cause

The `outputclass="iframe"` attribute is missing or misspelled on the `<object>` element.

### Fix

Open the DITA source. Confirm the `<object>` element has `outputclass="iframe"` (lowercase, exact spelling). Add or correct the attribute, then republish.

### Verification

Inspect the published page HTML. The output should contain an `<iframe src="...">` element at the expected location.

---

## Iframe renders as an HTML object element, not an iframe

### Symptom

The page renders an `<object>` or `<embed>` element instead of an `<iframe>`. The embedded content may not appear or may prompt for a plugin.

### Likely cause

The `outputclass="iframe"` attribute is missing. Without it, the Portal transform renders the `<object>` element as a standard HTML object element.

### Fix

Add `outputclass="iframe"` to the `<object>` element in the DITA source. Republish.

### Verification

Use browser developer tools to inspect the element. It should be `<iframe>`, not `<object>`.

---

## Iframe renders but embedded content is blank or shows an error

### Symptom

The iframe appears on the page at the correct height, but the embedded content area is blank, shows a loading spinner indefinitely, or shows a browser error such as "Refused to display ... in a frame."

### Likely cause

The third-party source is blocking embedding via `X-Frame-Options` or `Content-Security-Policy: frame-ancestors` headers. The source domain is configured to disallow iframe embedding from external domains.

### Fix

This is a third-party restriction. Options in order of likelihood:

1. **Use the embed URL, not the page URL.** Confirm you are using the embed-specific URL from the tool's share or embed dialog, not the URL from the browser address bar. Some tools allow embedding only via the embed URL.
2. **Check the tool's embed settings.** Some tools allow you to add authorized domains in the tool's share or embed configuration. Add your Portal domain.
3. **Contact the third-party provider.** If the tool does not support external embedding, there is no DITA-side workaround.

### Verification

Open the browser developer console. If you see a console error referencing `X-Frame-Options` or `frame-ancestors`, the block is confirmed. Resolved when the embedded content loads without that error.

---

## Content is cut off at the bottom of the iframe

### Symptom

The embedded content is visible but the bottom portion is hidden. Scrolling inside the iframe may or may not be available.

### Likely cause

The `height` attribute value is too small for the content.

### Fix

Increase the `height` value on the `<object>` element in the DITA source. Common adjustments:

- Add 50–100 pixels and republish.
- For Google Forms with many questions, try values between 800 and 1200.
- For Scribe tutorials, try 500–700.

Republish and preview after each adjustment.

### Verification

The embedded content renders completely visible without scrolling inside the iframe (unless scrolling is intentional for that content type).

---

## Iframe renders correctly locally but not in the published Portal

### Symptom

The embedded content displays correctly in a local preview or staging environment but does not render in the published Portal.

### Likely cause

The third-party tool's embed configuration may restrict the allowed domains to staging only, or the production Portal domain is not in the tool's authorized embedding list.

### Fix

In the third-party tool's embed or share settings, confirm that the production Portal domain is included in any domain allowlist. Some tools require explicit domain registration before allowing embedding from that domain.

### Verification

Open the published Portal page. The embedded content loads without console errors.

---

## PDF output contains a broken link or empty box where the iframe should be

### Symptom

When the same DITA content is published to PDF, the location where the iframe appears in Portal shows a broken element, placeholder text, or an empty box.

### Likely cause

The DITA `<object>` element with `outputclass="iframe"` is a Portal-specific rendering pattern. PDF transforms do not render HTML iframes and do not recognize the `outputclass="iframe"` instruction.

### Fix

This is a known limitation of the pattern. Options:

1. **Condition out the object element for PDF output.** Use DITA profiling attributes to exclude the `<object>` element from PDF publishing conditions.
2. **Add a fallback link.** Inside the `<object>` element, add `<desc>` or a plain-text link as fallback content for non-iframe outputs. Some transforms will render the fallback when the object cannot be displayed.

### Verification

The PDF output contains either the fallback content or no content at the iframe location, with no broken elements.

---

## DITA validation fails on the object element

### Symptom

The DITA editor or build tool reports a validation error on the `<object>` element or its attributes.

### Likely cause

The `<object>` element is placed in an invalid context (for example, inside a `<p>` element), or the `outputclass` attribute value is not recognized by a custom DTD or schema.

### Fix

1. Confirm the `<object>` element is inside `<body>`, `<section>`, or another valid block-level container—not inside `<p>` or inline elements.
2. If a custom DTD or schema restricts `outputclass` values, check whether `iframe` needs to be added to the allowed value list.

### Verification

The DITA source validates without errors in your authoring environment.
