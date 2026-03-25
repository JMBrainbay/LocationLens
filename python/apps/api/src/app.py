from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from config.env import get_settings
from integrations.index import build_providers
from lib.errors import ApiError, api_error_handler, unhandled_error_handler, validation_error_handler
from routes.debug import router as debug_router
from routes.compare import router as compare_router
from routes.health import router as health_router
from routes.places_profile import router as profile_router
from routes.places_resolve import router as resolve_router
from routes.places_suggest import router as suggest_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="nl-location-lens-api")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    providers = build_providers(settings)
    app.state.place_provider = providers["place_provider"]
    app.state.building_provider = providers["building_provider"]
    app.state.metrics_provider = providers["metrics_provider"]

    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    app.include_router(health_router)
    app.include_router(debug_router)
    app.include_router(suggest_router)
    app.include_router(resolve_router)
    app.include_router(profile_router)
    app.include_router(compare_router)

    return app


app = create_app()
