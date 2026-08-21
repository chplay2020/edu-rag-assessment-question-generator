from typing import Any
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.api.deps import get_db, get_current_active_lecturer
from app.models.user import User
from app.models.system import Export
from app.schemas.export_schema import ExportRequest, ExportListResponse
from app.services import question_bank_service, export_service
from app.core.storage import get_export_dir

logger = logging.getLogger(__name__)

router = APIRouter()

EXCEL_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

@router.post("/excel")
def export_questions_excel(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_lecturer),
):
    try:
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
        
        final_path, filename = export_service.export_questions_to_excel(
            db=db,
            questions=ordered_questions,
            user_id=current_user.id,
            question_ids=dedup_ids
        )
        
        return FileResponse(
            path=final_path,
            filename=filename,
            media_type=EXCEL_MEDIA_TYPE,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal error during export: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi hệ thống khi xuất file Excel."
        )


WORD_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

@router.post("/word")
def export_questions_word(
    request: ExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_lecturer),
):
    try:
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
        
        final_path, filename = export_service.export_questions_to_word(
            db=db,
            questions=ordered_questions,
            user_id=current_user.id,
            question_ids=dedup_ids
        )
        
        return FileResponse(
            path=final_path,
            filename=filename,
            media_type=WORD_MEDIA_TYPE,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal error during export Word: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi hệ thống khi xuất file Word."
        )
@router.get("", response_model=ExportListResponse)
def get_export_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_lecturer),
) -> Any:
    """Lấy danh sách lịch sử export của user hiện tại"""
    
    query = db.query(Export).filter(Export.exported_by == current_user.id)
    
    total = query.count()
    items = query.order_by(Export.created_at.desc()).offset(skip).limit(limit).all()
    
    return ExportListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{export_id}/download")
def download_export_file(
    export_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_lecturer),
):
    """Tải lại file Excel đã xuất trong lịch sử"""
    
    export_record = db.query(Export).filter(
        Export.id == export_id,
        Export.exported_by == current_user.id
    ).first()
    
    if not export_record:
        raise HTTPException(status_code=404, detail="Export not found")
        
    filename = export_record.file_path
    export_dir = get_export_dir()
    
    try:
        target_path = (export_dir / filename).resolve()
    except Exception as e:
        logger.warning(f"Path resolution error for {filename}: {e}")
        raise HTTPException(status_code=404, detail="Export not found")
        
    if not target_path.is_relative_to(export_dir.resolve()):
        logger.warning(f"Path traversal attempt blocked for user {current_user.id} accessing {filename}")
        raise HTTPException(status_code=404, detail="Export not found")
        
    if not target_path.exists():
        raise HTTPException(status_code=404, detail="Export not found")
        
    media_type = WORD_MEDIA_TYPE if filename.endswith('.docx') else EXCEL_MEDIA_TYPE
        
    return FileResponse(
        path=target_path,
        filename=filename,
        media_type=media_type,
    )
