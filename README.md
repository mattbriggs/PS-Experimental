# PS-Experimental

A collection of unsupported, experimental code produced by the Heretto Professional Services team. Nothing here is a Heretto product or official integration pathway.

> **Do not share with customers.** Code in this repository explores undocumented or restricted surfaces of Heretto CCMS. Review the `WARNING.md` file in each project before using any examples.

---

## Projects

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
