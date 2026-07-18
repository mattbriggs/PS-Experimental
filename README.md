# PS-Experimental

A collection of unsupported, experimental code produced by the Heretto Professional Services team. Nothing here is a Heretto product or official integration pathway.

> **Do not share with customers.** Code in this repository explores undocumented or restricted surfaces of Heretto CCMS. Review the `WARNING.md` file in each project before using any examples.

---

## Projects

### [MiddlewareAPI/](MiddlewareAPI/)

An experimental read-only middleware service that provides authenticated machine access to approved content resources stored in an internal WebDAV repository.

This project is intended to reduce direct programmatic use of WebDAV by placing a narrow, registry-gated HTTP API in front of approved Schematron and taxonomy assets.

**Includes:**
- [Package README](MiddlewareAPI/README.md) — package overview, setup, routes, and quality checks
- [Design docs](MiddlewareAPI/design/) — implementation notes, SRS material, and design references
- [Review and improvement plan](MiddlewareAPI/design/2027-07-17-improvment-implementation.md) — package audit, category scores, and implementation guidance to reach production quality
- [Docs](MiddlewareAPI/docs/) — architecture, API, deployment, and operations notes
- [Tests](MiddlewareAPI/tests/) — unit, integration, acceptance, security, and performance coverage

**Use cases covered:** list approved resources, retrieve registered files, enforce read-only access, validate public identifiers, and front WebDAV with an authenticated HTTP contract.

---

### [WebDav/](WebDav/)

Research and prototyping for programmatic access to Heretto CCMS via its WebDAV interface — the same connection point oXygen XML Editor uses under the hood.

Only oXygen is an approved WebDAV client. Direct programmatic use is not a supported integration pathway. This project exists to understand the surface, document its security implications, and propose a REST API deprecation path.

**Includes:**
- [Python examples](WebDav/python/) — standalone scripts and a reusable client module (`heretto_webdav`)
- [cURL examples](WebDav/curl/) — shell scripts for each WebDAV operation
- [Notes](WebDav/notes/) — research notes and a REST API deprecation proposal
- [WARNING.md](WebDav/WARNING.md) — scope and restrictions sourced from internal Slack and Confluence

**Use cases covered:** list resources, download, upload, delete, create directory, export taxonomy, sync/deploy schematron rules.

---

## Contributing

Add a top-level directory per project. Each project should include:

- `README.md` — what it does, prerequisites, setup
- `WARNING.md` — any scope restrictions or prohibited uses
- `.env.example` — credential placeholders (never commit a real `.env`)
