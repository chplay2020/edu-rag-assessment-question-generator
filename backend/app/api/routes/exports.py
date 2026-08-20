from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime

from app.api.deps import get_db, get_current_active_lecturer
from app.models.user import User
from app.schemas.export_schema import ExportRequest
from app.services import question_bank_service, export_service

router = APIRouter()

@router.post("/excel")
def export_questions_excel(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_lecturer),
):
    """Xuất danh sách câu hỏi ra file Excel (.xlsx)"""

    dedup_ids = list(dict.fromkeys(request.question_ids))
    
    questions = question_bank_service.get_exportable_questions(
        db, 
        current_user=current_user, 
        question_ids=dedup_ids,
        with_relations=True
    )
    
    # Restore order
    question_map = {q.id: q for q in questions}
    ordered_questions = [question_map[qid] for qid in dedup_ids if qid in question_map]
    
    # Generate workbook
    excel_stream = export_service.generate_excel_workbook(ordered_questions)
    
    # Return as StreamingResponse
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"questions_export_{timestamp}.xlsx"
    
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

