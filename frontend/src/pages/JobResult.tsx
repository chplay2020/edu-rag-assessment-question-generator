import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  CaretRight,
  CheckCircle,
  XCircle,
  CircleNotch,
  ArrowLeft,
  Lightbulb,
  WarningCircle,
  PencilSimple,
  ThumbsUp,
  ThumbsDown,
  X,
  Check,
  Plus,
} from '@phosphor-icons/react';
import { getCachedCourseById, fetchCourseById, type Course } from '../services/courseApi';
import { getCachedMaterialById, getMaterialById, type MaterialDetail } from '../services/materialApi';
import {
  getJobStatus,
  getJobQuestions,
  updateQuestion,
  reviewQuestion,
  type JobResponse,
  type QuestionResponse,
  type Option,
} from '../services/jobApi';
import './JobResult.css';

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

const difficultyMapEn: Record<string, string> = {
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard'
};

const bloomMapEn: Record<string, string> = {
  remember: 'Remember',
  understand: 'Understand',
  apply: 'Apply',
  analyze: 'Analyze',
  evaluate: 'Evaluate',
  create: 'Create'
};

// Editor Modal

interface EditorModalProps {
  isOpen: boolean;
  question: QuestionResponse | null;
  isEn?: boolean;
  onClose: () => void;
  onSave: (id: number, data: Parameters<typeof updateQuestion>[1]) => Promise<void>;
}

const EditorModal: React.FC<EditorModalProps> = ({ isOpen, question, isEn, onClose, onSave }) => {
  const [content, setContent] = useState('');
  const [explanation, setExplanation] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [bloomLevel, setBloomLevel] = useState('');
  const [options, setOptions] = useState<Option[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (question) {
      setContent(question.content);
      setExplanation(question.explanation ?? '');
      setDifficulty(question.difficulty);
      setBloomLevel(question.bloom_level);
      setOptions(question.options.map(o => ({ ...o })));
    }
  }, [question]);

  if (!isOpen || !question) return null;

  const handleCorrectChange = (optId: number) => {
    setOptions(opts => opts.map(o => ({ ...o, is_correct: o.id === optId })));
  };

  const handleOptionContentChange = (optId: number, val: string) => {
    setOptions(opts => opts.map(o => (o.id === optId ? { ...o, content: val } : o)));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await onSave(question.id, { content, explanation, difficulty, bloom_level: bloomLevel, options });
      onClose();
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="jr-modal-overlay" onClick={onClose}>
      <div className="jr-modal" onClick={e => e.stopPropagation()}>
        <div className="jr-modal-header">
          <h2 className="jr-modal-title">{isEn ? 'Edit question' : 'Chỉnh sửa câu hỏi'}</h2>
          <button className="jr-modal-close" onClick={onClose} aria-label="Đóng">
            <X size={18} />
          </button>
        </div>

        <div className="jr-modal-body">
          <div className="jr-form-group">
            <label className="jr-form-label">{isEn ? 'Question content' : 'Nội dung câu hỏi'}</label>
            <textarea
              className="jr-form-textarea"
              rows={4}
              value={content}
              onChange={e => setContent(e.target.value)}
            />
          </div>

          <div className="jr-form-group">
            <label className="jr-form-label">{isEn ? 'Options (select the correct one)' : 'Các đáp án (chọn đáp án đúng)'}</label>
            <div className="jr-options-editor">
              {options.map((opt, idx) => (
                <div className="jr-option-editor-row" key={opt.id}>
                  <input
                    type="radio"
                    name="correct-option"
                    checked={opt.is_correct}
                    onChange={() => handleCorrectChange(opt.id)}
                    aria-label={`Đáp án ${String.fromCharCode(65 + idx)} là đúng`}
                  />
                  <textarea
                    className="jr-form-textarea"
                    rows={2}
                    value={opt.content}
                    onChange={e => handleOptionContentChange(opt.id, e.target.value)}
                    style={{ resize: 'none' }}
                  />
                </div>
              ))}
            </div>
          </div>

          <div className="jr-form-group">
            <label className="jr-form-label">{isEn ? 'Explanation' : 'Giải thích'}</label>
            <textarea
              className="jr-form-textarea"
              rows={3}
              value={explanation}
              onChange={e => setExplanation(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <div className="jr-form-group" style={{ flex: 1 }}>
              <label className="jr-form-label">{isEn ? 'Difficulty' : 'Độ khó'}</label>
              <select className="jr-form-select" value={difficulty} onChange={e => setDifficulty(e.target.value)}>
                <option value="easy">{isEn ? 'Easy' : 'Dễ'}</option>
                <option value="medium">{isEn ? 'Medium' : 'Trung bình'}</option>
                <option value="hard">{isEn ? 'Hard' : 'Khó'}</option>
              </select>
            </div>
            <div className="jr-form-group" style={{ flex: 1 }}>
              <label className="jr-form-label">{isEn ? 'Bloom level' : 'Cấp độ Bloom'}</label>
              <select className="jr-form-select" value={bloomLevel} onChange={e => setBloomLevel(e.target.value)}>
                <option value="remember">{isEn ? 'Remember' : 'Nhớ (Remember)'}</option>
                <option value="understand">{isEn ? 'Understand' : 'Hiểu (Understand)'}</option>
                <option value="apply">{isEn ? 'Apply' : 'Vận dụng (Apply)'}</option>
                <option value="analyze">{isEn ? 'Analyze' : 'Phân tích (Analyze)'}</option>
                <option value="evaluate">{isEn ? 'Evaluate' : 'Đánh giá (Evaluate)'}</option>
                <option value="create">{isEn ? 'Create' : 'Sáng tạo (Create)'}</option>
              </select>
            </div>
          </div>
        </div>

        <div className="jr-modal-footer">
          <button className="jr-btn-secondary" onClick={onClose} disabled={isSaving}>
            {isEn ? 'Cancel' : 'Huỷ'}
          </button>
          <button className="jr-btn-primary" onClick={handleSave} disabled={isSaving}>
            {isSaving ? <CircleNotch size={16} className="cm-spin" /> : <Check size={16} />}
            {isEn ? 'Save changes' : 'Lưu thay đổi'}
          </button>
        </div>
      </div>
    </div>
  );
};

// Main page

export const JobResult: React.FC = () => {
  const { courseId, materialId, jobId } = useParams<{ courseId: string; materialId: string; jobId: string }>();

  const cId = Number(courseId);
  const mId = Number(materialId);
  const jId = Number(jobId);

  const [course, setCourse] = useState<Course | null>(getCachedCourseById(cId));
  const [material, setMaterial] = useState<MaterialDetail | null>(getCachedMaterialById(mId));
  const [job, setJob] = useState<JobResponse | null>(null);
  const [questions, setQuestions] = useState<QuestionResponse[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Editor modal state
  const [editingQuestion, setEditingQuestion] = useState<QuestionResponse | null>(null);

  // Review loading state per question
  const [reviewingId, setReviewingId] = useState<number | null>(null);

  const isEn = job?.config?.language === 'en';

  // Load course and material context
  useEffect(() => {
    async function loadContext() {
      try {
        const [c, m] = await Promise.all([fetchCourseById(cId), getMaterialById(mId)]);
        setCourse(c);
        setMaterial(m);
      } catch {
        setError('Không thể tải thông tin khóa học hoặc tài liệu.');
      }
    }
    loadContext();
  }, [cId, mId]);

  // Poll job status
  useEffect(() => {
    let timeoutId: number | undefined;

    async function checkJob() {
      try {
        const currentJob = await getJobStatus(jId);
        setJob(currentJob);

        if (currentJob.status === 'done') {
          const qs = await getJobQuestions(jId);
          setQuestions(qs);
        } else if (currentJob.status === 'failed') {
          setError(currentJob.error_message || 'Quá trình sinh câu hỏi thất bại.');
        } else {
          timeoutId = window.setTimeout(checkJob, 3000);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Lỗi khi tải thông tin tiến trình.');
      }
    }

    checkJob();
    return () => { if (timeoutId) window.clearTimeout(timeoutId); };
  }, [jId]);

  // Handlers
  const handleSaveEdit = useCallback(async (id: number, data: Parameters<typeof updateQuestion>[1]) => {
    const updated = await updateQuestion(id, data);
    setQuestions(qs => qs.map(q => (q.id === id ? updated : q)));
  }, []);

  const handleReview = useCallback(async (id: number, status: 'approved' | 'rejected') => {
    setReviewingId(id);
    try {
      await reviewQuestion(id, status);
      setQuestions(qs => qs.map(q => (q.id === id ? { ...q, status } : q)));
    } catch {

    } finally {
      setReviewingId(null);
    }
  }, []);

  // Error

  if (error && !job) {
    return (
      <div className="jr-container jr-centered">
        <WarningCircle size={48} weight="fill" className="jr-error-icon" />
        <h2>Đã có lỗi xảy ra</h2>
        <p>{error}</p>
        <Link to={`/courses/${cId}/materials/${mId}`} className="jr-btn-back">
          <ArrowLeft size={16} /> Quay lại tài liệu
        </Link>
      </div>
    );
  }

  const isLoadingJob = !job || job.status === 'pending' || job.status === 'running';

  return (
    <div className="jr-container">
      {/* Breadcrumb */}
      {course && material && (
        <nav className="cm-breadcrumb" aria-label="Breadcrumb" style={{ marginBottom: '24px' }}>
          <ol className="cm-breadcrumb-list">
            <li className="cm-breadcrumb-item">
              <Link to="/courses" className="cm-breadcrumb-link">Môn học</Link>
            </li>
            <li className="cm-breadcrumb-separator" aria-hidden="true"><CaretRight size={14} weight="bold" /></li>
            <li className="cm-breadcrumb-item">
              <Link to={`/courses/${cId}`} className="cm-breadcrumb-link cm-breadcrumb-course-name">{course.title}</Link>
            </li>
            <li className="cm-breadcrumb-separator" aria-hidden="true"><CaretRight size={14} weight="bold" /></li>
            <li className="cm-breadcrumb-item">
              <Link to={`/courses/${cId}/materials/${mId}`} className="cm-breadcrumb-link cm-breadcrumb-course-name">{material.title}</Link>
            </li>
            <li className="cm-breadcrumb-separator" aria-hidden="true"><CaretRight size={14} weight="bold" /></li>
            <li className="cm-breadcrumb-item">
              <span aria-current="page" className="cm-breadcrumb-current">Kết quả sinh câu hỏi</span>
            </li>
          </ol>
        </nav>
      )}

      {isLoadingJob ? (
        <div className="jr-state-card">
          <CircleNotch size={48} weight="bold" className="cm-spin jr-primary-icon" />
          <h2 className="jr-title">Đang sinh câu hỏi...</h2>
          <p className="jr-subtitle">AI đang phân tích tài liệu và tạo câu hỏi. Quá trình này có thể mất vài phút.</p>
        </div>
      ) : job?.status === 'failed' ? (
        <div className="jr-state-card">
          <XCircle size={48} weight="fill" className="jr-error-icon" />
          <h2 className="jr-title">Sinh câu hỏi thất bại</h2>
          <p className="jr-subtitle">{error || 'Quá trình sinh câu hỏi thất bại.'}</p>
          <div className="jr-actions-center">
            <Link to={`/courses/${cId}/materials/${mId}/generate`} className="jr-btn-primary">Thử lại</Link>
            <Link to={`/courses/${cId}/materials/${mId}`} className="jr-btn-secondary">Quay lại tài liệu</Link>
          </div>
        </div>
      ) : (
        <div className="jr-results-wrapper">
          {/* Page header */}
          <div>
            <div className="jr-header" style={{ alignItems: 'center', marginBottom: '12px' }}>
              <h1 className="jr-title" style={{ margin: 0 }}>{isEn ? 'Generated Questions' : 'Kết quả sinh câu hỏi'}</h1>
              <div className="jr-header-actions">
                <Link to={`/courses/${cId}/materials/${mId}/generate`} className="jr-btn-secondary">
                  <Plus size={16} />
                  {isEn ? 'Generate more' : 'Tạo thêm câu hỏi'}
                </Link>
              </div>
            </div>
            <p className="jr-subtitle" style={{ margin: 0 }}>
              {isEn ? `Successfully generated ${questions.length} questions from ` : `Đã tạo thành công ${questions.length} câu hỏi từ tài liệu `}
              <strong>{material?.title}</strong>.
            </p>
          </div>

          {/* Question list */}
          <div className="jr-question-list">
            {questions.map((q, index) => {
              const allWarnings: string[] = [];
              const llmScores: Record<string, number> = {};
              if (q.validation_results) {
                q.validation_results.forEach(res => {
                  if (res.warnings) allWarnings.push(...res.warnings);
                  if (res.validator_type === 'llm_judge' && res.score) {
                    Object.assign(llmScores, res.score);
                  }
                });
              }

              const getScoreClass = (score: number) => {
                if (score >= 0.8) return 'jr-score-high';
                if (score >= 0.5) return 'jr-score-medium';
                return 'jr-score-low';
              };

              const formatScore = (score: number) => Math.round(score * 100) + '%';

              const isReviewing = reviewingId === q.id;

              return (
                <div
                  key={q.id}
                  className={`jr-question-card ${allWarnings.length > 0 ? 'jr-card-has-warnings' : ''}`}
                >
                  {/* Card header */}
                  <div className="jr-question-header">
                    <span className="jr-question-number">{isEn ? 'Question' : 'Câu'} {index + 1}</span>
                    <div className="jr-question-badges">
                      <span className="jr-badge jr-badge-difficulty">{isEn ? 'Difficulty:' : 'Độ khó:'} {isEn ? (difficultyMapEn[q.difficulty] || q.difficulty) : (difficultyMap[q.difficulty] || q.difficulty)}</span>
                      <span className="jr-badge jr-badge-bloom">Bloom: {isEn ? (bloomMapEn[q.bloom_level] || q.bloom_level) : (bloomMap[q.bloom_level] || q.bloom_level)}</span>
                      {Object.entries(llmScores).map(([key, value]) => {
                        const label = key === 'grounding' ? 'Relevance' : key === 'clarity' ? 'Clarity' : key === 'assessment_quality' ? 'Correctness' : key;
                        return (
                          <span key={key} className={`jr-badge jr-badge-score ${getScoreClass(value)}`} title={`${key}: ${value}`}>
                            {label}: {formatScore(value)}
                          </span>
                        );
                      })}
                    </div>
                  </div>

                  {/* Warnings */}
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

                  {/* Body: question + options */}
                  <div className="jr-question-body">
                    <p className="jr-question-content">{q.content}</p>

                    <div className="jr-options-list">
                      {q.options.map((opt, optIndex) => (
                        <div
                          key={opt.id}
                          className={`jr-option-item ${opt.is_correct ? 'jr-option-correct' : ''}`}
                        >
                          <div className="jr-option-marker">{String.fromCharCode(65 + optIndex)}</div>
                          <div className="jr-option-text">{opt.content}</div>
                          {opt.is_correct && <CheckCircle size={18} weight="fill" className="jr-correct-icon" />}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Explanation */}
                  {q.explanation && (
                    <div className="jr-explanation-box">
                      <div className="jr-explanation-header">
                        <Lightbulb size={16} weight="fill" />
                        <strong>{isEn ? 'Explanation' : 'Giải thích'}</strong>
                      </div>
                      <p>{q.explanation}</p>
                    </div>
                  )}

                  {/* Source meta */}
                  {q.source_chunk_ids && q.source_chunk_ids.length > 0 && (
                    <div className="jr-source-meta">
                      {isEn ? 'Source segments:' : 'Tham chiếu từ các đoạn:'} {q.source_chunk_ids.join(', ')}
                    </div>
                  )}

                  {/* Action bar (T055 + T056) */}
                  <div className="jr-action-bar">
                    {q.status === 'approved' ? (
                      <span className="jr-status-pill approved">
                        <Check size={13} weight="bold" /> {isEn ? 'Approved' : 'Đã duyệt'}
                      </span>
                    ) : q.status === 'rejected' ? (
                      <span className="jr-status-pill rejected">
                        <X size={13} weight="bold" /> {isEn ? 'Rejected' : 'Đã từ chối'}
                      </span>
                    ) : null}

                    <button
                      id={`btn-edit-q${q.id}`}
                      className="jr-btn-edit"
                      onClick={() => setEditingQuestion(q)}
                      aria-label="Chỉnh sửa câu hỏi"
                    >
                      <PencilSimple size={14} />
                      {isEn ? 'Edit' : 'Chỉnh sửa'}
                    </button>

                    <button
                      id={`btn-approve-q${q.id}`}
                      className="jr-btn-approve"
                      onClick={() => handleReview(q.id, 'approved')}
                      disabled={isReviewing || q.status === 'approved'}
                      aria-label="Duyệt câu hỏi"
                    >
                      {isReviewing ? <CircleNotch size={14} className="cm-spin" /> : <ThumbsUp size={14} />}
                      {isEn ? 'Approve' : 'Duyệt'}
                    </button>

                    <button
                      id={`btn-reject-q${q.id}`}
                      className="jr-btn-reject"
                      onClick={() => handleReview(q.id, 'rejected')}
                      disabled={isReviewing || q.status === 'rejected'}
                      aria-label="Từ chối câu hỏi"
                    >
                      {isReviewing ? <CircleNotch size={14} className="cm-spin" /> : <ThumbsDown size={14} />}
                      {isEn ? 'Reject' : 'Từ chối'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: '12px' }}>
            <Link to={`/courses/${cId}/materials/${mId}`} className="jr-btn-back">
              <ArrowLeft size={16} />
              {isEn ? 'Back to material' : 'Quay lại tài liệu'}
            </Link>
          </div>
        </div>
      )}

      {/* Editor Modal */}
      <EditorModal
        isOpen={editingQuestion !== null}
        question={editingQuestion}
        isEn={isEn}
        onClose={() => setEditingQuestion(null)}
        onSave={handleSaveEdit}
      />
    </div>
  );
};
