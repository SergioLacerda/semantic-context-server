import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from semantic_context_server.config.environments import DEV, PROD, TEST, Environment

# ==========================================================
# constants
# ==========================================================

DEFAULT_ENVIRONMENT: Environment = DEV

ENV_FILE_BASE = ".env"
ENV_FILE_LOCAL = ".env.local"

# ==========================================================
# project root
# ==========================================================


def find_project_root(start: Path) -> Path:
    current = start.resolve()

    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent

    raise RuntimeError("Project root not found")


ROOT = find_project_root(Path(__file__).parent)


# ==========================================================
# env file discovery
# ==========================================================


def get_env_files(env: str) -> list[Path]:
    """
    Return ordered list of .env files to load.

    Priority (highest to lowest):
    1. .env.{env}.local
    2. .env.local
    3. .env.{env}
    4. .env
    """
    return [
        ROOT / f"{ENV_FILE_BASE}.{env}.local",
        ROOT / ENV_FILE_LOCAL,
        ROOT / f"{ENV_FILE_BASE}.{env}",
        ROOT / ENV_FILE_BASE,
    ]


# ==========================================================
# cli overrides
# ==========================================================


def parse_cli_overrides() -> dict[str, str]:
    overrides = {}

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


# ==========================================================
# environment loading
# ==========================================================


def load_environment() -> tuple[Environment, list[str], dict[str, str]]:
    """
    Prepara o processo carregando arquivos .env e CLI overrides para o os.environ.
    Este é o único lugar, junto com o SettingsLoader, que interage com o SO.

    Returns:
        - environment name
        - list of loaded file names
        - cli overrides dict
    """
    # 1. Detecta o ambiente base (único getenv permitido aqui para disparar o cascade)
    env_raw = os.getenv("ENVIRONMENT", DEFAULT_ENVIRONMENT).lower()
    if env_raw == "test":
        env = TEST
    elif env_raw == "prod":
        env = PROD
    else:
        env = DEV

    # 2. Carrega arquivos .env por ordem de prioridade (First Win)
    env_files = get_env_files(env)
    loaded_files = []

    for file in env_files:
        if file.exists():
            load_dotenv(dotenv_path=file, override=False)
            loaded_files.append(file.name)

    # 3. Aplica CLI Overrides (Sempre vencem os arquivos)
    cli_overrides = parse_cli_overrides()
    for k, v in cli_overrides.items():
        os.environ[k] = v

    return env, loaded_files, cli_overrides
