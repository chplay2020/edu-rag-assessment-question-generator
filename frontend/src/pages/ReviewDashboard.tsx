import React, { useState, useEffect, useCallback } from 'react';
import { getAllQuestions } from '../services/questionApi';
import type { QuestionResponse } from '../services/jobApi';
import { CheckCircle, PencilSimple, WarningCircle, Lightbulb, CaretDown, Check, X } from '@phosphor-icons/react';
import { ReviewActionButtons } from '../components/ReviewActionButtons';
import { QuestionEditorModal } from '../components/QuestionEditorModal';
import '../pages/JobResult.css';
import './ReviewDashboard.css';

const difficultyMap: Record<string, string> = {
  easy: 'Dễ',
  medium: 'Trung bình',
  hard: 'Khó'
};

const bloomMap: Record<string, string> = {
  remember: 'Nhớ',
  understand: 'Hiểu',
  apply: 'Vận dụng',
  analyze: 'Phân tích',
  evaluate: 'Đánh giá',
  create: 'Sáng tạo'
};

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
    <div className="rd-container" style={{ maxWidth: '900px', margin: '0 auto', padding: '32px 16px' }}>
      <div className="jr-header" style={{ alignItems: 'center', marginBottom: '24px' }}>
        <h1 className="jr-title" style={{ margin: 0 }}>Ngân hàng câu hỏi chờ duyệt</h1>
        <div className="rd-filters">
          <div className="jr-select-wrapper">
            <select className="jr-form-select" style={{ minWidth: '200px' }} value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
              <option value="">Tất cả trạng thái</option>
              <option value="draft">Nháp (Draft)</option>
              <option value="review_required">Chờ duyệt</option>
              <option value="approved">Đã duyệt</option>
              <option value="rejected">Từ chối</option>
            </select>
            <CaretDown size={14} className="jr-select-icon" />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="jr-state-card">
          <p>Đang tải...</p>
        </div>
      ) : (
        <div className="jr-question-list">
          {questions.map((q, index) => {
            const allWarnings: string[] = [];
            if (q.validation_results) {
              q.validation_results.forEach(res => {
                if (res.warnings) allWarnings.push(...res.warnings);
              });
            }

            return (
            <div key={q.id} className={`jr-question-card ${allWarnings.length > 0 ? 'jr-card-has-warnings' : ''}`}>
              <div className="jr-question-header">
                <span className="jr-question-number">Câu {index + 1}</span>
                <div className="jr-question-badges">
                  {q.status === 'approved' && <span className="jr-status-pill approved"><Check size={13} weight="bold" /> Đã duyệt</span>}
                  {q.status === 'rejected' && <span className="jr-status-pill rejected"><X size={13} weight="bold" /> Từ chối</span>}
                  {q.status === 'draft' && <span className="jr-status-pill" style={{backgroundColor: '#e2e3e5', color: '#383d41'}}>Nháp</span>}
                  {q.status === 'review_required' && <span className="jr-status-pill" style={{backgroundColor: '#fff3cd', color: '#856404'}}>Chờ duyệt</span>}
                  
                  <span className="jr-badge jr-badge-difficulty">Độ khó: {difficultyMap[q.difficulty] || q.difficulty}</span>
                  <span className="jr-badge jr-badge-bloom">Bloom: {bloomMap[q.bloom_level] || q.bloom_level}</span>
                </div>
              </div>

              {allWarnings.length > 0 && (
                <div className="jr-warnings-box">
                  <div className="jr-warnings-header">
                    <WarningCircle size={16} weight="fill" />
                    <strong>Cảnh báo chất lượng ({allWarnings.length})</strong>
                  </div>
                  <ul className="jr-warnings-list">
                    {allWarnings.map((warn, wIdx) => (
                      <li key={wIdx}>{warn}</li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="jr-question-body">
                <p className="jr-question-content">{q.content}</p>
                <div className="jr-options-list">
                  {q.options.map((opt, optIndex) => (
                    <div key={opt.id} className={`jr-option-item ${opt.is_correct ? 'jr-option-correct' : ''}`}>
                      <div className="jr-option-marker">{String.fromCharCode(65 + optIndex)}</div>
                      <div className="jr-option-text">{opt.content}</div>
                      {opt.is_correct && <CheckCircle size={18} weight="fill" className="jr-correct-icon" />}
                    </div>
                  ))}
                </div>
              </div>

              {q.explanation && (
                <div className="jr-explanation-box">
                  <div className="jr-explanation-header">
                    <Lightbulb size={16} weight="fill" />
                    <strong>Giải thích</strong>
                  </div>
                  <p>{q.explanation}</p>
                </div>
              )}
              
              <div className="jr-action-bar">
                <button
                  className="jr-btn-edit"
                  onClick={() => setEditingQuestion(q)}
                  aria-label="Chỉnh sửa câu hỏi"
                >
                  <PencilSimple size={14} /> Chỉnh sửa
                </button>
                <ReviewActionButtons questionId={q.id} currentStatus={q.status} onSuccess={handleReviewSuccess} />
              </div>
            </div>
          )})}
          {questions.length === 0 && <div className="jr-state-card"><p>Không có câu hỏi nào.</p></div>}
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
