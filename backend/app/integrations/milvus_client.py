class MilvusGateway:
    """Placeholder for vector index interactions (dedup, semantic search)."""

    def __init__(self, uri: str = "http://milvus:19530"):
        self.uri = uri

    async def upsert_embedding(self, *, object_id: str, vector: list[float], modality: str) -> None:
        # TODO: integrate pymilvus in the next iteration.
        _ = (object_id, vector, modality)
        return None

    async def search_similar(self, *, vector: list[float], top_k: int = 5) -> list[dict]:
        # TODO: return nearest neighbors from Milvus collection.
        _ = (vector, top_k)
        return []
