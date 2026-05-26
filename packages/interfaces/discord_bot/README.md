# packages/interfaces/discord_bot

Discord transport package.

Status:
- extracted-partial
- package now owns canonical `create_bot` bootstrap implementation
- legacy wrappers in `src/semantic_context_server/frameworks/discord/*` removed
- remaining migration: move supporting modules from `src/semantic_context_server/interfaces/discord/*` into package namespace
