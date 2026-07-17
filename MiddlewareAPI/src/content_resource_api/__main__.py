"""Entry point for running the API server directly."""

import uvicorn

from content_resource_api.config.settings import Settings


def main() -> None:
    settings = Settings()
    uvicorn.run(
        "content_resource_api.interface.http.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=8080,
        log_level=settings.app_log_level.lower(),
        workers=1,
    )


if __name__ == "__main__":
    main()
