from celery import Celery

from app.core.config import settings

celery_app = Celery("prepoai", broker=settings.redis_dsn, backend=settings.redis_dsn)


@celery_app.task(name="etl.import_data")
def etl_import_data(file_uri: str, project_id: int) -> dict:
    """Long-running ETL placeholder task for large dataset imports."""
    return {
        "status": "queued",
        "message": "ETL pipeline placeholder finished",
        "file_uri": file_uri,
        "project_id": project_id,
    }
