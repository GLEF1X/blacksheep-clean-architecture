import pathlib

from dynaconf import Dynaconf
from fastapi import FastAPI

from web import api

BASE_DIR = pathlib.Path(__name__).resolve().parent.parent

settings = Dynaconf(
    settings_files=['settings.toml', '.secrets.toml'],
    redis=True,
    preload=[BASE_DIR / "settings.toml"],
    environments=["development", "production", "testing"],
    load_dotenv=False,
)


def configure_application() -> FastAPI:
    application = FastAPI()
    api.v1.install_v1_api(application.router)
    return application


app = configure_application()
