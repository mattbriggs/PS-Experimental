# CCMS Config-as-Code: Approach Review

## Approach Assessment

Your document is well-structured and pragmatic. The config-as-code model (YAML → validated XML → manifest-driven WebDAV deploy) addresses real pain points that have been documented repeatedly across Heretto's internal pages. The emphasis on a hard scope boundary between customer-managed and SaaS-managed paths is the right instinct and the single most important safety property.

---

## Similar Projects & Prior Art

| Project | Status | Relevance |
|---------|--------|-----------|
| **WebDAV Deprecation** (2022) | Stalled / unresolved | Explored replacing WebDAV with an Oxygen plugin or admin UI. Debate never fully concluded. Your proposal *retains* WebDAV as the deployment transport. |
| **DEVOPS-1062 – Config folder automation** | Submitted, no target date | DevOps ticket to automate portal config folder creation. Same problem space as your pilot. |
| **CCMS versioning & time to production** | Concept/discussion | Engineering doc proposing faster deployment pipelines for the ezd codebase. Same underlying drivers: auditability, reproducibility, rollback. |
| **CCMS Test Automation (Playwright + Bruno)** | Active (Jul 2025) | Environment-independent test suites with externalized config. Closest analog to "config as data" thinking. |
| **Redirects Script** | Shipped | PowerShell tooling to generate portal redirect config from old/new site structures. Small proof that scripted config generation works in this ecosystem. |
| **CMS API-v2 Feature Brief** | In progress | Building a full public REST API. Could eventually provide a deployment transport that replaces WebDAV. |

### References

- [WebDAV Deprecation](https://jorsek.atlassian.net/wiki/spaces/PM/pages/1538097171/WebDAV+Deprecation)
- [Portal Development Environments](https://jorsek.atlassian.net/wiki/spaces/CDT/pages/1840381953/Portal+Development+Environments)
- [CCMS versioning and time to production](https://jorsek.atlassian.net/wiki/spaces/EN/pages/1689452559/Heretto+CCMS+versioning+and+time+to+production)
- [CCMS Test Automation (Playwright)](https://jorsek.atlassian.net/wiki/spaces/QA/pages/2269315073/CCMS+Test+Automation+Playwright)
- [Redirects Script](https://jorsek.atlassian.net/wiki/spaces/CDT/pages/1856176129/Redirects+Script)
- [CMS API-v2](https://jorsek.atlassian.net/wiki/spaces/PM/pages/1845428225/Feature+Brief+-+CMS+API-v2)

---

## Documented Objections (from WebDAV Deprecation Discussion)

These were raised in 2022 and are still relevant to any project that touches the same surface area:

1. **"WebDAV is table stakes for a DITA CMS"** – Matt Hallman argued that Paligo and competitors support WebDAV, so removing or restricting it weakens the product. Your proposal *uses* WebDAV as a transport rather than removing it, but the allowlist restrictions could collide with this expectation if scoped too narrowly.

2. **"Performance issues are eXist, not the protocol"** – Several engineers pushed back on the claim that WebDAV is inherently slow. If your deployment step is slow, it may not be the pipeline's fault.

3. **"Make a better replacement and prove it's better"** – Michael Stover's position: don't deprecate something without a clearly superior alternative that people choose on its own merits.

4. **"Open-ended API dependency"** – Karin Cross flagged that building tooling against APIs that may not exist or may change is risky scope creep. Applies to your builder if it eventually needs deeper CCMS integration.

5. **"Separate internal vs. customer use cases"** – Casey Jordan insisted the internal configuration use case (CSM editing XML) is distinct from customer file access. Your proposal seems scoped to the internal case, which is good, but clarifying this up front will preempt the same debate.

---

## Risks (Institutional + Technical)

| Risk | Source | Covered in Doc? |
|------|--------|:---:|
| **Config drift** – people editing deployed XML directly via Oxygen/WebDAV | Versioning doc, templates/configs page | ✅ |
| **Hardcoded org IDs** in config XML (e.g., `content-management.xml`) require per-customer fixups | [CCMS templates and configs](https://jorsek.atlassian.net/wiki/spaces/QA/pages/2273607681/CCMS+templates+and+configs) | Partially (environment overlays) |
| **Cache clear + config reload** required after any config change (`/tools/dev/dev.xql`) | [CCMS Reload Configs](https://jorsek.atlassian.net/wiki/spaces/QA/pages/1900216343/CCMS+Reload+Configs) | ❌ Not addressed |
| **Multi-version CCMS estate** – different customers on different versions may have different XML schemas | Versioning doc | ❌ Not addressed |
| **WebDAV as transport is already under strategic question** – if Admin UI or REST API replaces it, your pipeline's deployment layer has to be rewritten | WebDAV Deprecation, CMS API-v2 | ❌ Not addressed |
| **No documented path inventory** – the exact set of "customer-managed WebDAV directories" hasn't been publicly catalogued | None found | Flagged as prerequisite |
| **Partial deployment / atomicity** – config reload between steps could surface incomplete state | Reload Configs page | ✅ |
| **Oxygen locking** – if files are locked by someone's stale Oxygen session, deploy will fail | WebDAV Deprecation comments | ❌ Not addressed |

---

## Recommendations

1. **Address the cache/reload step in your pipeline.** The config reload (`Upload SDK 2 → Clear org cache → Reload Configuration`) is a mandatory post-deploy step. Your deployment manifest should include it, or at minimum document that it's a manual follow-up.

2. **Acknowledge the WebDAV transport question.** Your architecture is sound regardless of the underlying protocol, but noting that the deployment layer is pluggable (WebDAV today, REST API tomorrow) will prevent the same "why WebDAV?" debate from stalling adoption.

3. **Pilot on workflow configuration.** Based on what I see in the templates/configs page, workflows and user configs are the highest-volume repetitive patterns. Workflow XML is also fully customer-managed with no SaaS mutation, making it the safest pilot target.

4. **Map the hardcoded org-ID problem early.** The QA process already documents that some clients have hardcoded org IDs in `content-management.xml`. Your YAML model needs an explicit `org_id` field and the builder must substitute it correctly per environment.

5. **Add a lock-check pre-flight.** Before deploying, verify no target files have active WebDAV locks. Fail fast if they do.

---

## Summary

The document is a strong basis for a team decision. The main gaps are around post-deploy cache reload, the strategic uncertainty of WebDAV as a long-term transport, and multi-version compatibility. All are solvable within the pilot scope if called out explicitly.
