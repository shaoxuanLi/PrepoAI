class ObjectStorageGateway:
    """Placeholder object storage client for MinIO/S3."""

    def __init__(self, endpoint: str = "http://minio:9000", bucket: str = "prepoai"):
        self.endpoint = endpoint
        self.bucket = bucket

    async def put_object(self, *, object_name: str, data: bytes, content_type: str) -> str:
        # TODO: integrate boto3/minio SDK in the next iteration.
        _ = (data, content_type)
        return f"{self.endpoint}/{self.bucket}/{object_name}"
