from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_interface, get_pg_session
from app.schemas.domain import QualityMetricCreate, QualityMetricRead
from app.services.quality_service import compute_f1
from backend_db.db_interface import DBInterface
from backend_db.db_models import QualityMetric

router = APIRouter()


@router.post("/metric", response_model=QualityMetricRead)
async def record_quality_metric(
    payload: QualityMetricCreate,
    dbi: DBInterface = Depends(get_db_interface),
) -> QualityMetric:
    return await dbi.record_quality_metric(
        task_assignment_id=payload.task_assignment_id,
        annotator_id=payload.annotator_id,
        reviewer_id=payload.reviewer_id,
        metric_type=payload.metric_type,
        score=payload.score,
        detail_json=payload.detail_json,
        note=payload.note,
    )


@router.get("/overview")
async def quality_overview(pg: AsyncSession = Depends(get_pg_session)) -> dict:
    total = (await pg.execute(select(func.count(QualityMetric.id)))).scalar() or 0
    avg_score = (await pg.execute(select(func.avg(QualityMetric.score)))).scalar() or 0.0
    f1_preview = compute_f1(precision=0.9, recall=0.85)

    return {
        "total_metrics": int(total),
        "avg_score": round(float(avg_score), 4),
        "sample_human_f1_formula_result": round(f1_preview, 4),
    }
