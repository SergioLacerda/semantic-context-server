# config/environments.py

from typing import Literal

Environment = Literal["test", "dev", "prod"]

TEST: Environment = "test"
DEV: Environment = "dev"
PROD: Environment = "prod"
