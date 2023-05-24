from os import getenv
from pathlib import Path

from dotenv import load_dotenv


# Env possible paths in order that they should be called
env_paths = [Path(__file__).parent.parent / ".env", Path(__file__).parent / ".env"]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)

DB_NAME_PREFIX = getenv("DB_NAME_PREFIX", "ldt_pik_local_dev_")

# LOCAL_RUN = getenv("LOCAL_RUN", "False").lower() in ("true", "1", "t")
CONTAINER_RUN = getenv("CONTAINER_RUN", "False").lower() in ("true", "1", "t")

if CONTAINER_RUN:
    POSTGRES_HOST = getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(getenv("POSTGRES_PORT", 5432))
else:
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = int(getenv("POSTGRES_PORT_ON_HOST", 5432))
POSTGRES_USER = getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_MAX_CONNECTIONS = int(getenv("POSTGRES_MAX_CONNECTIONS", 5))

APP_PREFIX = getenv("API_PREFIX", "/api/v1")
APP_PORT = int(getenv("APP_PORT", 8095))

BASE_DIR = Path(__file__).parent

SECRET_KEY = getenv(
    "SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
)
HASHING_ALGORITHM = getenv("HASHING_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))
