WebDAV is only the file access protocol. Your permission model and scope boundaries have to be enforced by the server, not by WebDAV itself. The practical design is: authenticate the caller, map that identity to an allowed root path plus allowed operations, and reject anything outside that boundary before the WebDAV layer touches storage.

**Core model**

Use three separate concepts in your SDK and server design:

1. `Authentication`
The client proves identity with `username`, `password`, and/or `token`.

2. `Authorization`
The server decides what that identity may do:
`read`, `write`, `delete`, `move`, `copy`, `lock`, `unlock`, `mkcol`, `propfind`, `proppatch`.

3. `Scope`
The server limits the identity to one or more path prefixes, for example:
`/customers/acme/`
`/products/widget-a/`
`/projects/docs/`

A good mental model is: every credential resolves to a policy object like:

```json
{
  "principal": "alice",
  "allowedRoots": ["/content/acme/"],
  "allowedMethods": ["GET", "HEAD", "OPTIONS", "PROPFIND", "PUT", "MKCOL"],
  "denyDelete": true,
  "readOnly": false
}
```

**Important constraint**

WebDAV clients can still attempt any path they want. Scope limiting is not a client feature. It is a server-side enforcement feature. Never rely on the client to stay in its folder.

**Recommended auth approach**

For interoperability, especially with desktop DAV clients like Oxygen, the safest model is:

- Use HTTPS only.
- Use HTTP authentication compatible with standard WebDAV clients.
- Treat the token as either:
  - an app-specific password, or
  - a personal access token used in place of the password.

That is usually more interoperable than requiring a custom login flow.

Practical options:

- `Basic over TLS`
  Username + password or username + token.
  Easiest for DAV client compatibility.

- `Bearer token`
  Good for SDK/programmatic clients.
  Less universally friendly for generic DAV desktop tools unless they let users set raw headers.

Because Oxygen is a primary client, I would bias toward:
- `username + token` as the real interoperable path
- regular password only for human login if needed
- avoid requiring both password and token on every DAV request unless you know all clients support it cleanly

**Permission design**

Keep permissions simple and path-based. WebDAV clients do many background operations, so overcomplicated rules become hard to debug.

Recommended permission dimensions:

- `read metadata`
  Needed for `PROPFIND`
- `read content`
  Needed for `GET`
- `write content`
  Needed for `PUT`
- `create collections`
  Needed for `MKCOL`
- `delete`
  Needed for `DELETE`
- `rename/move`
  Needed for `MOVE`
- `copy`
  Needed for `COPY`
- `properties edit`
  Needed for `PROPPATCH`
- `locking`
  Needed for `LOCK` / `UNLOCK`

Then derive roles such as:

- `reader`
- `editor`
- `publisher`
- `admin`

Example:

- `reader`: `OPTIONS`, `HEAD`, `GET`, `PROPFIND`
- `editor`: reader + `PUT`, `MKCOL`, `MOVE`, `COPY`
- `publisher`: editor + `DELETE`, `PROPPATCH`
- `admin`: all DAV methods inside assigned roots

**Scope limiting**

This is the critical part for CCMS safety.

Enforce all of the following:

- Canonicalize the requested path before authorization.
- Reject path traversal attempts.
- Resolve aliases/symlinks carefully if your storage layer allows them.
- Check both source and destination paths for `MOVE` and `COPY`.
- Apply rules recursively to descendants of the allowed root.
- Return `403 Forbidden` for in-scope but unauthorized actions.
- Return `404 Not Found` when you do not want callers to infer existence outside scope.

A strong rule is:

- A principal may only access paths where `requestedPath` starts with one of `allowedRoots`.
- For `MOVE` and `COPY`, both `sourcePath` and `destinationPath` must be allowed.

**Oxygen-specific practical note**

Oxygen and similar WebDAV clients usually depend on standard DAV behavior, not CCMS-specific semantics. That means your server should behave predictably for:

- `OPTIONS`
- `PROPFIND`
- `GET`
- `PUT`
- `MKCOL`
- `DELETE`
- `MOVE`
- `COPY`
- optional `LOCK` / `UNLOCK`

If permission checks are too strict on `PROPFIND`, many clients will appear broken even though file content permissions are fine. Metadata access is often required just to browse.

**SDK notes**

Your SDK should hide WebDAV quirks and expose a clean policy-aware API.

Recommended SDK concerns:

- Auth configuration
  - username/password
  - username/token
  - bearer token
- Base URL
- Root scope awareness
- Method wrappers
  - `list(path)`
  - `stat(path)`
  - `read(path)`
  - `write(path, content)`
  - `mkdir(path)`
  - `delete(path)`
  - `move(src, dst)`
  - `copy(src, dst)`
- Error normalization
  - `AuthenticationError`
  - `AuthorizationError`
  - `ScopeError`
  - `ConflictError`
  - `NotFoundError`
  - `PreconditionFailedError`

Example SDK config:

```ts
const client = new WebDavClient({
  baseUrl: "https://ccms.example.com/dav",
  auth: {
    username: "alice",
    token: "pat_123"
  }
});
```

Example server-facing behavior:

- Send token as password for DAV-compatible clients.
- For programmatic clients, optionally allow `Authorization: Bearer`.

**What to document for SDK consumers**

Document these rules clearly:

- All access is restricted to the user’s assigned content roots.
- A successful login does not imply access to the whole repository.
- Some clients may see `404` for out-of-scope paths by design.
- `MOVE` and `COPY` require permission on both source and destination.
- `PROPFIND` may succeed where `GET` does not, depending on policy.
- Tokens should be preferred over reusable account passwords.
- HTTPS is mandatory.

**Recommended server policy**

If you want the simplest reliable model:

- One DAV endpoint
- HTTPS only
- Token-based auth, optionally entered as the password
- Each token bound to:
  - one principal
  - one or more root paths
  - one role
  - optional expiration
- Server enforces scope on every request
- Log every denied request with:
  - principal
  - method
  - normalized path
  - denial reason

That is the cleanest design for both Oxygen and SDK clients.

If useful, I can turn this into a short SDK design note or a formal integration spec with example request/response patterns.