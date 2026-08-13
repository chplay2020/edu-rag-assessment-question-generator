from datetime import datetime, timezone

from app.models.material import Job
from app.schemas.material_schema import JobResponse


def test_job_response_matches_job_model_contract():
    created_at = datetime.now(timezone.utc)
    finished_at = datetime.now(timezone.utc)
    job = Job(
        id=1,
        material_id=10,
        task_type="process_material",
        status="done",
        created_at=created_at,
        finished_at=finished_at,
    )

    response = JobResponse.model_validate(job)

    assert response.id == 1
    assert response.material_id == 10
    assert response.task_type == "process_material"
    assert response.status == "done"
    assert response.created_at == created_at
    assert response.finished_at == finished_at
