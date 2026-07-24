# PS-Experimental

An internal repository of Heretto Professional Services experiments, playbooks, prototypes, and design material. Some directories contain executable code, while others capture implementation guidance, research, or early-stage architecture work.

> **Do not share with customers by default.** Parts of this repository describe unsupported or restricted Heretto CCMS surfaces. Review each project's local documentation before reusing or circulating any material.

---

## Repository at a glance

| Path | Type | Current state |
|---|---|---|
| [MiddlewareAPI/](MiddlewareAPI/) | Python service | Experimental read-only API with tests, deployment assets, and operational docs |
| [WebDav/](WebDav/) | Research + code examples | Programmatic WebDAV exploration with Python and cURL examples |
| [iFrame-on-Page/](iFrame-on-Page/) | Internal playbook | Field-tested DITA pattern for embedding iframes in Heretto Portal pages |
| [Infra-as-Code/](Infra-as-Code/) | Design and planning | Configuration-as-code analysis for customer-managed CCMS XML workflows |
| [_source/](_source/) | Shared source material | Reference notes, pattern-library content, and raw supporting material |

---

## Projects

### [MiddlewareAPI/](MiddlewareAPI/)

An experimental read-only middleware service that provides authenticated machine access to approved content resources stored in an internal WebDAV repository.

This project is the most implementation-heavy area in the repo. It narrows access to approved Schematron and taxonomy assets through a registry-gated HTTP API rather than allowing arbitrary WebDAV access.

**Includes:**
- [Package README](MiddlewareAPI/README.md) — setup, routes, configuration, and quality checks
- [Docs](MiddlewareAPI/docs/) — architecture, API overview, deployment, and operations guidance
- [Design docs](MiddlewareAPI/design/) — implementation notes, SRS material, and review artifacts
- [Tests](MiddlewareAPI/tests/) — unit, integration, acceptance, security, and performance coverage
- [Deploy assets](MiddlewareAPI/deploy/) — Kubernetes and Prometheus configuration

**Use cases covered:** list approved resources, retrieve registered files, enforce read-only access, validate public identifiers, and front WebDAV with an authenticated HTTP contract.

---

### [WebDav/](WebDav/)

Research and prototyping for programmatic access to Heretto CCMS through its WebDAV interface, which is the same transport layer used by oXygen XML Editor.

This area documents the raw surface directly, along with its risks, and serves as background for safer replacement patterns such as the middleware API.

**Includes:**
- [Project README](WebDav/README.md) — overview, security considerations, and REST replacement proposal
- [Python examples](WebDav/python/) — standalone scripts plus a reusable `heretto_webdav` client
- [cURL examples](WebDav/curl/) — one script per WebDAV operation
- [Notes](WebDav/notes/) — research notes and implementation findings
- [WARNING.md](WebDav/WARNING.md) — scope restrictions and prohibited use guidance

**Use cases covered:** list resources, download, upload, delete, create directories, export taxonomies, and sync or deploy Schematron rules.

---

### [iFrame-on-Page/](iFrame-on-Page/)

An internal implementation playbook for embedding iframe content inside Heretto Portal pages using DITA `<object>` markup with `outputclass="iframe"`.

Unlike the WebDAV and middleware work, this directory is primarily delivery guidance rather than a software package. It packages validated examples, authoring instructions, troubleshooting notes, and provenance for a field-tested Portal pattern.

**Includes:**
- [Playbook README](iFrame-on-Page/readme.md) — overview, quick start, constraints, and revision history
- [Docs](iFrame-on-Page/docs/) — concept, implementation, troubleshooting, and security guidance
- [Examples](iFrame-on-Page/examples/) — copy-ready DITA topic and map samples
- [Notes](iFrame-on-Page/notes/) — original source material and governance analysis
- [Design](iFrame-on-Page/design/) — background material for standardizing the pattern

**Use cases covered:** embed third-party forms, guided walkthroughs, and interactive demos in published Portal pages.

---

### [Infra-as-Code/](Infra-as-Code/)

Early-stage design work for a safer configuration-as-code workflow around customer-managed CCMS XML.

This directory currently contains planning and analysis material rather than executable tooling. The focus is on separating configuration intent from generated XML artifacts, enforcing deployment boundaries, and designing a reproducible release process for WebDAV-deployed configuration.

**Includes:**
- [Two-pager](Infra-as-Code/notes/2-pager.md) — problem framing, solution direction, and implementation outline
- [Technical notes](Infra-as-Code/notes/) — architecture and review material
- [Design](Infra-as-Code/design/) — SRS content and supporting design artifacts

**Use cases covered:** configuration generation strategy, validation workflow design, controlled deployment, verification, and rollback planning.

---

## Shared source material

### [_source/](_source/)

A support directory for raw inputs and reusable internal references used to develop the other projects in this repository.

**Includes:**
- [_source/playbook-guidance.md](_source/playbook-guidance.md) — packaging guidance for implementation playbooks
- [_source/pattern-library.txt](_source/pattern-library.txt) — pattern reference material
- [_source/CCMSAPI.txt](_source/CCMSAPI.txt) — source notes related to CCMS API thinking

---

## Working conventions

Top-level directories in this repository do not all have the same shape. Some are codebases, while others are research or playbook packages. In practice, each project should include:

- `README.md` or equivalent landing document
- Supporting docs, notes, examples, or design material appropriate to the project type
- `WARNING.md` when the material covers prohibited, unsupported, or otherwise sensitive implementation surfaces
- `.env.example` when executable code requires local configuration
