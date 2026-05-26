from typing import Any


class ANNPrefilter:
    priority = 40

    def __init__(self, ann: Any = None) -> None:
        """
        ann: objeto que implementa search() ou route()
        """
        self.ann = ann

    async def run(self, ctx: Any) -> Any:
        if not ctx.q_vec or not self.ann:
            return ctx

        try:
            # -----------------------------------------
            # padrão moderno: search direto
            # -----------------------------------------
            if hasattr(self.ann, "search"):
                docs = self.ann.search(ctx.q_vec)

                ctx.candidates = [d["id"] if isinstance(d, dict) else d for d in docs]

                if ctx.candidates:
                    return ctx

            # -----------------------------------------
            # fallback: route (IVF clássico)
            # -----------------------------------------
            if hasattr(self.ann, "route"):
                cluster_ids = self.ann.route(ctx.q_vec)

                candidates: list[Any] = []
                for cid in cluster_ids:
                    candidates.extend(getattr(self.ann, "inverted_lists", {}).get(cid, []))

                if candidates:
                    ctx.candidates = candidates

        except Exception:
            # 🔥 nunca quebra pipeline
            pass

        return ctx
