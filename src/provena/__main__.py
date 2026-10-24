"""`provena` / `python -m provena`: run the API server."""

import uvicorn

from provena.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "provena.api.app:create_app",
        factory=True,
        host=settings.host,
        port=settings.port,
        log_config=None,
        reload=settings.env == "development",
    )


if __name__ == "__main__":
    main()
