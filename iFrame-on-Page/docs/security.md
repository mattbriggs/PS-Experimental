# Security principles for embedded iframes in Heretto Portal

Embedding third-party content in a documentation portal is not the same as linking to it. A link invites the reader to leave the page; an iframe brings external content into the page, where it executes in the reader's browser session alongside the documentation itself. The principles below address the security and privacy risks that distinction creates and describe how to evaluate and mitigate them in the context of Heretto Portal.

---

## An iframe inherits the trust context of the page that hosts it

When a browser renders an embedded iframe, it creates a separate browsing context for the embedded document, but that context sits nested within the host page's environment. The embedded content and the host page share the user's browser session: authentication cookies scoped to the Portal domain are present in the browser alongside whatever the iframe is doing, and the user's browser history, storage, and network requests reflect activity from both. Modern browsers enforce the same-origin policy, which prevents the embedded frame from directly reading the host page's cookies or DOM. That boundary is meaningful, but it does not eliminate the risk that embedded content poses.

Within those constraints, an iframe serving compromised or deceptive content can cause significant harm. It can display false instructions that override the surrounding documentation, initiate file downloads, open popup windows, or redirect the user's attention in ways that damage trust in the documentation portal. The user has no visible indication that embedded content originates from a different domain than the rest of the page, and trust, once broken, attaches to the Portal itself rather than to the third-party source the author embedded. The host page is responsible for everything the reader encounters on it, including the content of every iframe on that page. Understanding this dynamic is the foundation for every other security decision involved in embedding third-party content.

---

## Embed only content from sources you have independently verified

The URL in the `data` attribute of a DITA `<object>` element becomes the content served to every reader who views that Portal page. Verification is not a one-time task completed by recognizing a domain name. It requires confirming that the embed URL comes from the tool's documented share or embed dialog, that the account publishing the content is controlled by your organization or a named vendor, and that the embedded content does not collect user information, display advertising, or solicit action outside the intended purpose of the embed.

Informal delivery channels compound the risk considerably. An embed URL that arrives through a Slack message, a forwarded email, or a customer request may or may not point to the service the sender intended. URL shorteners, redirect chains, and recently registered domains all warrant additional scrutiny before a URL is committed to DITA source. The commit amplifies exposure: once embedded in a published Portal page, a compromised URL will serve malicious or misleading content to every subsequent reader until an author identifies the problem, corrects the source, and republishes. The cost of verification before authoring is minutes; the cost of remediation after publication can be considerably greater.

Third-party services are also subject to change independent of authoring activity. A vendor acquired by a different company, a free tier discontinued and redirected to an upsell page, or a service account with an expired subscription can each result in an embed URL serving content the original author never intended. Periodic review of live embedded content is part of the ongoing responsibility that comes with embedding rather than linking.

---

## Use HTTPS for every embed URL

All embed URLs must begin with `https://`. An HTTP embed URL loaded inside an HTTPS Portal page creates a mixed-content condition that modern browsers resolve by blocking the embedded resource entirely—or, in older browser configurations, by silently downgrading the page's effective security level. Neither outcome is acceptable: the first breaks embedded content for the reader without explanation; the second exposes the reader's session to network-level interception without any visible warning.

HTTPS also provides the foundational guarantee that the content the browser receives is the content the origin server sent. Without transport-layer encryption, an attacker positioned between the reader and the embed source can modify the embedded content in transit—injecting scripts, replacing form submission targets, or altering the displayed instructions before the reader ever sees them. The tools validated for this pattern (Google Forms, Scribe, and Navattic) all serve content over HTTPS and publish HTTPS embed URLs through their documented share dialogs. Any embed URL that does not begin with `https://` should be treated as invalid and not committed to DITA source.

---

## Apply the sandbox attribute to limit what embedded content can do

The HTML `<iframe>` element supports a `sandbox` attribute that restricts what embedded content is permitted to do, regardless of what the content itself requests. Without additional permissions, a sandboxed iframe cannot run scripts, submit forms, open popup windows, navigate the top-level browser window, or access cookies and local storage. The principle at work is not that embedded content is untrustworthy by default—it is that sandboxing forces an explicit decision about what the content needs, and that explicit decision is far preferable to an implicit grant of all iframe capabilities.

Authors embedding read-only content—video players, static tutorials, display-only demos—can apply `sandbox` with no additional permissions, accepting that the restrictions are compatible with the content's purpose. Authors embedding interactive content—forms that must submit data, demos that require JavaScript—must grant specific capabilities using the attribute's `allow-*` token syntax rather than removing `sandbox` entirely to resolve a rendering problem. The sandbox attribute is passed to Heretto Portal's output transform as a `<param>` element on the DITA `<object>`: `<param name="sandbox" value="allow-scripts allow-forms"/>`, with only the tokens the content requires. Verify that your Portal publishing profile passes this attribute through to the rendered iframe before relying on it in production.

Removing `sandbox` entirely to debug an embed that is not behaving correctly is a common shortcut. Leaving that removal in place for production publishing is a common mistake, and one that reintroduces the full surface of iframe risk. The discipline of granting only what the embed requires is the practice this principle is designed to establish and maintain.

---

## Confirm how the third-party tool handles user data before embedding it in documentation

A Portal page that embeds a form, a demo, or a tutorial is also embedding the data-collection and tracking behavior of the tool that serves it. Readers who interact with embedded content may be submitting data to a third-party system whose privacy policy, data residency, and retention practices are governed entirely outside the documentation team's control. For documentation portals serving regulated industries—or portals subject to GDPR, CCPA, or comparable frameworks—this is not a peripheral consideration.

Before embedding any tool that accepts user input, confirm that the tool's data handling practices are compatible with the Portal's privacy commitments. The relevant factors include the tool's published privacy policy, the geographic residency of collected data, whether the tool places tracking cookies or uses browser fingerprinting, and whether readers have meaningful notice that they are interacting with a third-party service. The seamlessness of the embed is precisely what makes disclosure important: the reader has no visible indicator that submitting a form sends data to Google's servers, or that completing a Scribe tutorial logs session data to Scribe's infrastructure.

Even tools that do not accept form responses may load third-party analytics, advertising scripts, or social tracking pixels as part of the embed payload. Reviewing the tool's documentation for what the embed loads—not only what it visually displays—is the appropriate level of verification for any documentation portal that has made privacy commitments to its readers. That review, like source verification, is a condition of embedding, not an optional step taken after content is already published.
