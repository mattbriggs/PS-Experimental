# Authoring Schematron Rules via WebDAV

## Overview

Customers with valid Heretto CCMS credentials can access and author Schematron
schema files directly through a WebDAV connection — no Oxygen license is
required. Any WebDAV-compatible file manager (Windows Explorer, macOS Finder,
WinSCP, Cyberduck, etc.) can be used to browse and edit the configuration files
on the CCMS instance.

## Prerequisites

- Active Heretto CCMS user credentials with WebDAV access permissions
- A WebDAV-compatible file manager or text/XML editor that supports WebDAV
  connections (e.g., Cyberduck, WinSCP, Windows Explorer mapped drive, macOS
  Finder "Connect to Server")
- Knowledge of Schematron ISO/IEC 19757-3 (or Schematron 2.0) syntax

## Connecting to Configuration Files via WebDAV

1. Open your WebDAV-compatible client.
2. Create a new WebDAV connection using the following URL pattern:

   ```
   https://<your-instance>.easydita.com/webdav/db/organizations/<org>/configuration
   ```

3. Authenticate with your Heretto CCMS username and password.
4. Once connected, navigate to the schematron configuration location within:

   ```
   organizations/<org>/configuration/
   ```

   Schematron files (`.sch`) reside in the org's configuration directory.

## Schematron File Structure

A valid Schematron file follows this hierarchy:

```xml
<schema xmlns="http://purl.oclc.org/dml/schematron"
        queryBinding="xslt2"
        schemaVersion="1.0">
  <title>My Custom Rules</title>

  <pattern id="category-id">
    <title>Category Name</title>

    <rule context="XPath-to-element" id="rule-id">
      <assert test="XPath-condition" id="assert-id">
        Error message displayed to authors when condition fails.
      </assert>
      <report test="XPath-condition" id="report-id">
        Warning message displayed when condition is true.
      </report>
    </rule>

  </pattern>
</schema>
```

### Key Elements and Attributes

| Element     | Key Attributes                                           | Purpose                                 |
|-------------|----------------------------------------------------------|-----------------------------------------|
| `<schema>`  | `id`, `defaultPhase`, `queryBinding`, `schemaVersion`    | Root element; sets processing language  |
| `<pattern>` | `id`, `abstract`, `is-a`                                 | Groups rules into a category            |
| `<rule>`    | `context` (required XPath), `id`, `abstract`             | Defines the context node(s) to check    |
| `<assert>`  | `test` (required XPath), `id`, `role`, `flag`            | Fires message when test is **false**    |
| `<report>`  | `test` (required XPath), `id`, `role`, `flag`            | Fires message when test is **true**     |

### Tips

- Set `queryBinding="xslt2"` for XPath 2.0 support.
- Give every `<assert>` and `<report>` a unique `id` — this enables tracking
  individual rule violations in the Content Quality reports.
- The `<pattern>` maps to a **category** in the Heretto UI; the `<rule>/@id`
  maps to the issue type.

## Saving and Activating Schema Changes

After editing and saving your `.sch` file back to the WebDAV location, a
**system reset** (configuration reload) is required for the CCMS to pick up the
changes.

### Current Reload Process

> **Important:** There is currently no public REST API endpoint to trigger the
> configuration reload programmatically. The reload must be performed by a
> **system administrator** via the internal admin tools page.

The process is:

1. Log in to the CCMS instance as a **system admin**.
2. Navigate to the Org configuration and SDK page:

   ```
   https://<instance>.easydita.com/tools/dev/dev.xql
   ```

3. Execute the following actions **in order**:
   - Select **"Clear org cache"**
   - Select **"Reload Configuration"**

### Who Can Perform the Reload?

| Scenario                                  | Who fires the reset?          |
|-------------------------------------------|-------------------------------|
| Customer **does not** have sysadmin access | CDS team fires the reset      |
| Customer **has** sysadmin access           | Customer can self-serve        |

### Is There an API for This?

As of current documentation, **no public API call exists** to trigger the
configuration reload. The CMS API v2 roadmap includes expanding REST API
coverage, but a reload/reset endpoint is not yet documented or available.

If a programmatic approach is needed, the options to investigate are:

- Whether `/tools/dev/dev.xql` accepts direct HTTP GET/POST calls (it is an
  XQuery endpoint — it may respond to authenticated requests without the UI)
- Future CMS API v2 coverage for admin operations

**For now, the standard path is: customer edits schema → notifies CDS → CDS
fires Clear org cache + Reload Configuration.**

## Workflow Summary

```
┌─────────────────────────────────────────────────────────┐
│ 1. Customer connects to WebDAV                          │
│ 2. Customer edits/creates .sch file in configuration/   │
│ 3. Customer saves file via WebDAV                       │
│ 4. CDS (or sysadmin) fires system reset:               │
│    a. Clear org cache                                   │
│    b. Reload Configuration                              │
│ 5. Schematron rules are active in the editor            │
└─────────────────────────────────────────────────────────┘
```
