import uvicorn

from app import app
from config.env import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)


if __name__ == "__main__":
    main()
