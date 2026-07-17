# Request Flow

## Successful resource retrieval

```
Client ──GET /schematron/rules.sch──► CorrelationIdMiddleware
                                          │ attaches/generates X-Correlation-ID
                                          ▼
                                      get_principal (FastAPI dep)
                                          │ extracts X-API-Key header
                                          │ ApiKeyAuthAdapter.authenticate()
                                          │ → ClientPrincipal{client_id, scopes}
                                          ▼
                                      get_schematron route handler
                                          │ validate_public_filename("rules.sch")
                                          │ → ok (no traversal, no encoded sep)
                                          ▼
                                      GetResourceHandler.handle()
                                          │ registry.get_resource("schematron","rules.sch")
                                          │ → RegisteredResource{upstream_object, size_limit}
                                          │ auth_service.authorize(principal, resource)
                                          │ → AuthorizationDecision{allowed=True}
                                          │ repository.get_metadata(upstream_ref)
                                          │ → ResourceMetadata{etag, last_modified, ...}
                                          │ size check: content_length <= size_limit_bytes
                                          │ cond_service.evaluate(etag, if_none_match, ...)
                                          │ → CacheDecision{serve_full=True}
                                          │ repository.open_stream(upstream_ref)
                                          │ → AsyncIterator[bytes]
                                          ▼
                                      StreamingResponse(200)
                                          │ ETag: "abc123"
                                          │ Content-Type: application/xml
                                          │ X-Correlation-ID: <id>
                                          ▼
Client ◄── 200 bytes ───────────────────
```

## 304 Not Modified (ETag match)

Same flow through `GetResourceHandler.handle()`, but after `get_metadata`:

```
cond_service.evaluate(etag='"abc123"', if_none_match='"abc123"', ...)
→ CacheDecision{not_modified=True, etag='"abc123"'}
→ NotModifiedResult{etag='"abc123"'}
→ Response(304, ETag: "abc123", no body)
```

`If-None-Match` evaluation always precedes `If-Modified-Since`.

## Authentication failure (missing key)

```
Client ──GET /schematron ──► CorrelationIdMiddleware
                                 ▼
                             get_principal()
                                 │ no X-API-Key, no Authorization header
                                 │ → raises MissingCredential
                                 ▼
                             domain_error_handler()
                                 │ MissingCredential → HTTP 401
                                 │ ErrorResponse{error_code, message, correlation_id}
                                 ▼
Client ◄── 401 ─────────────────
```

The WebDAV repository is never contacted on authentication failures.
