# packages/interfaces/http_api

HTTP transport package.

Status:
- extracted-partial
- package owns app bootstrap (`create_app`) and router composition (`api_router`)
- legacy wrapper `src/semantic_context_server/app.py` removed
- still depends on legacy middleware/lifecycle and route controller modules from `src/interfaces/api/*`
