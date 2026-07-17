That makes sense. A lightweight middleware API is the right call here — you just need a thin layer that:
Exposes specific resources (schematron rules, taxonomy files) via simple endpoints
Handles authentication properly at the server level (not relying on client identity)
Scopes access to only the paths/resources that should be available programmatically

Something like a few GET endpoints that proxy the relevant files from the WebDAV instance with proper auth, rather than giving clients direct WebDAV access to everything. This gives you:
Controlled surface area — only the resources you explicitly expose are reachable
Scriptability — simple HTTP GETs that work with curl, Python requests, CI/CD pipelines, etc.
Auditability — you can log who accessed what without parsing WebDAV logs
No client dependency — no Oxygen requirement, no browser-based WebDAV exposure

It avoids the overhead of a full REST API with CRUD operations, versioning, pagination, etc. — you're really just serving specific files through an authenticated, scoped gateway.