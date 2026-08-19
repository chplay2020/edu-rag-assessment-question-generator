import React, { useState, useEffect, useCallback } from 'react';
import { getAllQuestions } from '../services/questionApi';
import type { QuestionResponse } from '../services/jobApi';
import { CheckCircle, PencilSimple } from '@phosphor-icons/react';
import { ReviewActionButtons } from '../components/ReviewActionButtons';
import { QuestionEditorModal } from '../components/QuestionEditorModal';
import './ReviewDashboard.css';

export const ReviewDashboard: React.FC = () => {
  const [questions, setQuestions] = useState<QuestionResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [editingQuestion, setEditingQuestion] = useState<QuestionResponse | null>(null);

  const fetchQuestions = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAllQuestions(filterStatus ? { status: filterStatus } : {});
      setQuestions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filterStatus]);

  useEffect(() => {
    fetchQuestions();
  }, [fetchQuestions]);

  const handleReviewSuccess = () => {
    fetchQuestions(); // Refresh list after review action
  };

  return (
    <div className="rd-container">
      <div className="rd-header">
        <h1>Ngân hàng câu hỏi chờ duyệt</h1>
        <div className="rd-filters">
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="">Tất cả trạng thái</option>
            <option value="draft">Nháp (Draft)</option>
            <option value="review_required">Chờ duyệt (Review Required)</option>
            <option value="approved">Đã duyệt (Approved)</option>
            <option value="rejected">Từ chối (Rejected)</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p>Đang tải...</p>
      ) : (
        <div className="rd-question-list">
          {questions.map((q) => (
            <div key={q.id} className="rd-question-card card-panel">
              <div className="rd-question-header">
                <div className="rd-question-badges">
                  <span className={`rd-badge rd-badge-${q.status}`}>{q.status}</span>
                  <span className="rd-badge">Độ khó: {q.difficulty}</span>
                </div>
                <div className="rd-question-actions">
                  <button className="rd-btn-icon" onClick={() => setEditingQuestion(q)} title="Chỉnh sửa">
                    <PencilSimple size={20} />
                  </button>
                </div>
              </div>
              <p className="rd-question-content">{q.content}</p>
              
              <div className="rd-options-list">
                {q.options.map((opt, optIndex) => (
                  <div key={opt.id} className={`rd-option-item ${opt.is_correct ? 'rd-option-correct' : ''}`}>
                    <div className="rd-option-marker">{String.fromCharCode(65 + optIndex)}</div>
                    <div className="rd-option-text">{opt.content}</div>
                    {opt.is_correct && <CheckCircle size={20} weight="fill" className="rd-correct-icon" />}
                  </div>
                ))}
              </div>
              
              <div className="rd-footer-actions">
                <ReviewActionButtons questionId={q.id} currentStatus={q.status} onSuccess={handleReviewSuccess} />
              </div>
            </div>
          ))}
          {questions.length === 0 && <p>Không có câu hỏi nào.</p>}
        </div>
      )}

      {editingQuestion && (
        <QuestionEditorModal
          question={editingQuestion}
          onClose={() => setEditingQuestion(null)}
          onSuccess={() => {
            setEditingQuestion(null);
            fetchQuestions();
          }}
        />
      )}
    </div>
  );
};
