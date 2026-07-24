# Embed an iframe: step-by-step guide

## Before you start

Collect the following before authoring:

- **Embed URL**: the URL your third-party tool provides for iframe embedding. This is usually labeled "embed," "share," or "embed code" in the tool's share settings. Copy only the URL portion, not the full `<iframe>` HTML tag.
- **Required height**: the height in pixels the embedded content needs to display correctly. Most tools specify a recommended height in their embed instructions. Start with the recommended value; adjust after previewing in Portal.
- **Target topic**: the DITA topic where the iframe will appear.

---

## Step 1: Get the embed URL

The embed URL is not the same as the page URL of the content. Most tools provide a separate embed URL through a share or embed dialog.

| Tool | Where to find the embed URL |
|---|---|
| Google Forms | Form editor → Send → Embed → copy the `src` value from the `<iframe>` tag |
| Scribe | Published guide → Share → Embed → copy the URL from the `src` attribute |
| Navattic | Flow editor → Share → Embed → copy the URL from the `src` attribute |
| Loom | Video page → Share → Embed → copy the URL from the `src` attribute |
| YouTube | Video page → Share → Embed → copy the URL from the `src` attribute |

If the tool gives you a complete `<iframe>` HTML tag, extract only the `src` URL. That URL is the value for the `data` attribute on your DITA `<object>` element.

---

## Step 2: Determine the height

Set the `height` attribute to a pixel value that fits the content. Use the tool's recommended embed height when provided.

| Content type | Typical height |
|---|---|
| Google Form (short) | 600 |
| Google Form (long) | 800 |
| Scribe tutorial | 400–600 |
| Navattic product demo | 600–800 |
| Loom video | 360–480 |
| YouTube video | 315–480 |

These are starting values. Preview in Portal and adjust if content is cut off or the iframe is taller than the content.

---

## Step 3: Add the object element to your DITA topic

In your DITA topic, place the `<object>` element inside a `<section>` or directly inside `<body>`. Add a `<title>` to the enclosing `<section>` if the section does not already have one—this helps readers understand what the embedded content is before it loads.

```xml
<section id="your-section-id">
  <title>Section title</title>
  <object
    data="YOUR_EMBED_URL"
    height="600"
    outputclass="iframe">
    <param name="frameborder" value="0"/>
    <param name="width" value="100%"/>
    <param name="allowfullscreen"/>
  </object>
</section>
```

Replace `YOUR_EMBED_URL` with the embed URL you copied in step 1. Replace `600` with the height you chose in step 2.

### Attribute reference

| Attribute | Required | Value | Purpose |
|---|---|---|---|
| `data` | Yes | Embed URL | The URL of the embedded content |
| `height` | Yes | Pixel integer | Controls the iframe height |
| `outputclass` | Yes | `iframe` | Tells the Portal transform to render an iframe instead of an object element |
| `frameborder` param | Recommended | `0` | Removes the default border around the iframe |
| `width` param | Recommended | `100%` | Makes the iframe fill its container width |
| `allowfullscreen` param | Optional | (no value) | Enables full-screen mode for content that supports it |

---

## Step 4: Validate your DITA

Confirm that the `<object>` element is valid in your DITA environment before publishing:

- The element must be inside `<body>`, `<section>`, or another block-level container. It is not valid inside `<p>` or inline elements.
- The `data` attribute must be a complete URL starting with `https://`.
- The `outputclass` attribute value is case-sensitive. Use `iframe`, not `Iframe` or `IFRAME`.

If your DITA editor validates against the DITA 1.3 DTD, the `<object>` element is valid and should pass validation without errors.

---

## Step 5: Publish to Portal and verify

After publishing:

1. Open the published Portal page in a browser.
2. Confirm the iframe renders and the third-party content loads.
3. If the iframe renders but shows a blank area or a browser error, see [troubleshooting.md](troubleshooting.md).
4. Adjust the `height` value if content is cut off at the bottom and republish.

---

## Adapt this pattern to other content sources

Any tool that provides an embed URL can use this pattern. The DITA authoring steps are the same regardless of the content source. Only the `data` URL and `height` value change.

To embed content that is not publicly accessible (behind authentication), confirm that the authenticated user's session will carry over to the embedded context. Most third-party tools handle this automatically when the user is signed in, but some require additional configuration in the tool's embed settings.
