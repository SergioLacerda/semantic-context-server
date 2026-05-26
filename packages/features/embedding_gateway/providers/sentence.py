from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Iterable
from typing import Any, cast

from packages.core.shared_kernel.resilience import resilient_call

logger = logging.getLogger("packages.features.embedding_gateway.sentence")


def _load_backend() -> tuple[Any, Any]:
    try:
        import torch
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer, torch
    except ImportError as err:
        raise ImportError("sentence-transformers or torch not installed") from err


def _detect_device(device: str | None, torch: Any) -> str:
    if device:
        device = device.lower()
        valid = {"cpu", "cuda", "mps"}
        if device not in valid:
            raise ValueError(f"Invalid device '{device}'. Expected {valid}")
        return device
    if torch and torch.cuda.is_available():
        return "cuda"
    if torch and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def _auto_batch_size(device: str) -> int:
    if device == "cuda":
        return 128
    if device == "mps":
        return 64
    return 16


class SentenceEmbeddingProvider:
    supports_batch = True

    def __init__(
        self,
        model: str,
        device: str | None = None,
        batch_size: int | None = None,
        timeout: float = 180.0,
    ) -> None:
        SentenceTransformer, torch = _load_backend()
        self._torch = torch
        self.model_name = model
        self.device = _detect_device(device, torch)
        self.batch_size = batch_size or _auto_batch_size(self.device)
        self.timeout = timeout

        logger.info(
            "Embedding config → model=%s device=%s batch_size=%s timeout=%s",
            self.model_name,
            self.device,
            self.batch_size,
            self.timeout,
        )

        self.model = SentenceTransformer(model, device=self.device)
        self.is_e5 = "e5" in model.lower()
        self._dimension: int = self.model.get_sentence_embedding_dimension()
        self._semaphore = asyncio.Semaphore(2)

    @property
    def dimension(self) -> int | None:
        return self._dimension

    def _prepare_doc(self, text: str) -> str:
        return "passage: " + text if self.is_e5 else text

    def _encode_single(self, text: str) -> Any:
        if self._torch:
            with self._torch.no_grad():
                return self.model.encode(text, normalize_embeddings=True)
        return self.model.encode(text)

    def _encode_batch(self, texts: list[str]) -> Any:
        if self._torch:
            with self._torch.no_grad():
                return self.model.encode(
                    texts,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                    normalize_embeddings=True,
                )
        return self.model.encode(texts)

    async def _run_in_thread(self, fn: Callable[..., Any], *args: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, fn, *args)

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            return [0.0] * self._dimension

        text = self._prepare_doc(text)

        async def call() -> list[float]:
            async with self._semaphore:
                vec = await self._run_in_thread(self._encode_single, text)
                return cast(list[float], vec.tolist())

        try:
            return cast(list[float], await resilient_call(call))
        except Exception:
            logger.exception("Sentence embedding failed")
            raise

    async def embed_batch(
        self,
        texts: Iterable[str],
        *,
        concurrency: int = 5,
    ) -> list[list[float]]:
        texts_list = [t for t in texts if t and t.strip()]
        if not texts_list:
            return []

        if self.is_e5:
            texts_list = ["passage: " + t for t in texts_list]

        async def call() -> list[list[float]]:
            async with self._semaphore:
                vectors = await self._run_in_thread(self._encode_batch, texts_list)
                return [v.tolist() for v in vectors]

        try:
            return cast(list[list[float]], await resilient_call(call))
        except Exception:
            logger.exception("Sentence batch embedding failed")
            raise


def create_sentence_embedding(**kwargs: Any) -> SentenceEmbeddingProvider:
    model = kwargs.get("model")
    if not isinstance(model, str):
        raise ValueError("'model' must be a string")
    return SentenceEmbeddingProvider(
        model=model,
        device=kwargs.get("device"),
        batch_size=kwargs.get("batch_size"),
    )
