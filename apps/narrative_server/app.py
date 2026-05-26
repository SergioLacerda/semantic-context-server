"""Composition entrypoint for narrative server app.

Wave 2.12 runtime composition currently delegates to package interfaces while
preserving legacy implementation compatibility.
"""

from packages.interfaces.http_api import app, create_app

__all__ = ["app", "create_app"]
