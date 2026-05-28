import os
import sys
from pathlib import Path

from dotenv import load_dotenv

Environment = str
TEST = "test"
DEV = "dev"
PROD = "prod"

DEFAULT_ENVIRONMENT: Environment = DEV

ENV_FILE_BASE = ".env"
ENV_FILE_LOCAL = ".env.local"


def find_project_root(start: Path) -> Path:
    current = start.resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Project root not found")


ROOT = find_project_root(Path(__file__).parent)


def get_env_files(env: str) -> list[Path]:
    return [
        ROOT / f"{ENV_FILE_BASE}.{env}.local",
        ROOT / ENV_FILE_LOCAL,
        ROOT / f"{ENV_FILE_BASE}.{env}",
        ROOT / ENV_FILE_BASE,
    ]


def parse_cli_overrides() -> dict[str, str]:
    overrides: dict[str, str] = {}
    for arg in sys.argv:
        if not arg.startswith("--"):
            continue
        if "=" not in arg:
            continue
        parts = arg[2:].split("=", 1)
        if len(parts) != 2 or not parts[0] or not parts[1]:
            continue
        key, value = parts
        overrides[key.upper()] = value
    return overrides


def load_environment() -> tuple[Environment, list[str], dict[str, str]]:
    env_raw = os.getenv("ENVIRONMENT", DEFAULT_ENVIRONMENT).lower()
    if env_raw == TEST:
        env = TEST
    elif env_raw == PROD:
        env = PROD
    else:
        env = DEV

    env_files = get_env_files(env)
    loaded_files: list[str] = []

    for file in env_files:
        if file.exists():
            load_dotenv(dotenv_path=file, override=False)
            loaded_files.append(file.name)

    cli_overrides = parse_cli_overrides()
    for key, value in cli_overrides.items():
        os.environ[key] = value

    return env, loaded_files, cli_overrides
