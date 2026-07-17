# Context: System Landscape

The Content Resource API sits between internal tooling clients and the WebDAV
repository that stores authoritative Schematron rules and taxonomy files.

```
┌─────────────────────────────────────────────────────────────────┐
│                       Heretto Platform                           │
│                                                                  │
│  ┌──────────────┐    X-API-Key     ┌──────────────────────────┐ │
│  │  CI/CD tool  │ ─────────────►  │                          │ │
│  └──────────────┘                  │  Content Resource API    │ │
│                                    │  (this service)          │ │
│  ┌──────────────┐    X-API-Key     │                          │ │
│  │  Script/bot  │ ─────────────►  │  - API key auth          │ │
│  └──────────────┘                  │  - Registry lookup       │ │
│                                    │  - Streaming proxy       │ │
│                                    └────────────┬─────────────┘ │
│                                                 │               │
│                                                 │ WebDAV/HTTPS  │
│                                                 ▼               │
│                                    ┌──────────────────────────┐ │
│                                    │  Internal WebDAV          │ │
│                                    │  - Schematron rules       │ │
│                                    │  - Taxonomy files         │ │
│                                    └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Key design decisions

- **Read-only**: the API never writes to WebDAV; all HTTP methods except GET return 405.
- **Registry-gated**: only resources explicitly registered in the registry YAML are reachable.
  Clients cannot enumerate or traverse the WebDAV tree.
- **No path passthrough**: upstream WebDAV paths are never disclosed to clients.
  The registry maps public filenames to private upstream objects.
- **Stateless**: each replica is identical. No session state or sticky routing required.
