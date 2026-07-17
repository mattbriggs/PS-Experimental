# Secret Rotation

## API key rotation

There is no zero-downtime rotation without a brief overlap window. Plan during a
low-traffic period or maintain two active keys simultaneously.

1. Add the new key to the secret store: `API_KEY_<client-id>=scope:read,...`
2. Notify the client of the new key value (out-of-band)
3. Restart the service to load the new environment variable
4. Client switches to the new key
5. Remove the old key from the secret store
6. Restart again to clear the old key

## WebDAV password rotation

1. Update the credential on the WebDAV server
2. Update `APP_WEBDAV_PASSWORD` in the secret store
3. Restart the API service
4. Verify: `GET /api/resources/v1/health/ready` returns 200
