from semantic_context_server.infrastructure.storage.vector.chroma_vector_store import (
    ChromaVectorStore,
)


class MockCollection:
    def __init__(self):
        self.storage = {}

    def add(self, ids, embeddings):
        for i, emb in zip(ids, embeddings, strict=True):
            self.storage[i] = emb

    def get(self, ids=None):
        if ids:
            return {
                "ids": ids,
                "embeddings": [self.storage.get(i) for i in ids],
            }
        return {"ids": list(self.storage.keys())}

    def query(self, query_embeddings, n_results):
        if not self.storage:
            return {}

        ids = list(self.storage.keys())[:n_results]
        return {"ids": [ids]}

    def delete(self, where):
        self.storage.clear()


class DummyCollection:
    def __init__(self):
        self.data = {}
        self.last_query = None

    def add(self, ids, embeddings):
        self.data[ids[0]] = embeddings[0]

    def get(self):
        return {"ids": list(self.data.keys())}

    def query(self, query_embeddings, n_results):
        self.last_query = (query_embeddings, n_results)

        if not self.data:
            return {"ids": [[]]}

        return {"ids": [[list(self.data.keys())[0]]]}


def test_add_and_keys():
    store = ChromaVectorStore(DummyCollection())

    store.add("doc1", [1, 0])

    assert "doc1" in store.keys()


def test_search_returns_expected_key():
    collection = DummyCollection()
    store = ChromaVectorStore(collection)

    store.add("doc1", [1, 0])

    result = store.search([1, 0], k=1)

    assert result == ["doc1"]


def test_search_calls_query_correctly():
    collection = DummyCollection()
    store = ChromaVectorStore(collection)

    store.add("doc1", [1, 0])

    store.search([1, 0], k=2)

    assert collection.last_query == ([[1, 0]], 2)


def test_add_and_get():
    collection = MockCollection()
    store = ChromaVectorStore(collection)

    store.add("doc1", [1.0, 2.0])

    result = store.get("doc1")

    assert result == [1.0, 2.0]


def test_get_returns_none_when_missing():
    class EmptyCollection:
        def get(self, ids=None):
            return {}

    store = ChromaVectorStore(EmptyCollection())

    result = store.get("doc1")

    assert result is None


def test_keys_with_data():
    collection = MockCollection()
    store = ChromaVectorStore(collection)

    store.add("a", [1])
    store.add("b", [2])

    keys = store.keys()

    assert set(keys) == {"a", "b"}


def test_keys_empty():
    class EmptyCollection:
        def get(self):
            return {}

    store = ChromaVectorStore(EmptyCollection())

    keys = store.keys()

    assert keys == []


def test_search_with_results():
    collection = MockCollection()
    store = ChromaVectorStore(collection)

    store.add("doc1", [1])
    store.add("doc2", [2])

    result = store.search([1], k=1)

    assert len(result) == 1


def test_search_no_results():
    class EmptyCollection:
        def query(self, query_embeddings, n_results):
            return {}

    store = ChromaVectorStore(EmptyCollection())

    result = store.search([1], k=1)

    assert result == []


def test_clear():
    collection = MockCollection()
    store = ChromaVectorStore(collection)

    store.add("doc1", [1])
    store.clear()

    assert collection.storage == {}
