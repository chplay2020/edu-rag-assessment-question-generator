import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CaretRight, CheckCircle, XCircle, CircleNotch, ArrowLeft, Lightbulb, WarningCircle } from '@phosphor-icons/react';
import { getCachedCourseById, fetchCourseById, type Course } from '../services/courseApi';
import { getCachedMaterialById, getMaterialById, type MaterialDetail } from '../services/materialApi';
import { getJobStatus, getJobQuestions, type JobResponse, type QuestionResponse } from '../services/jobApi';
import './JobResult.css';

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

  // Load course and material context
  useEffect(() => {
    async function loadContext() {
      try {
        const [c, m] = await Promise.all([
          fetchCourseById(cId),
          getMaterialById(mId)
        ]);
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
          // Fetch questions
          const qs = await getJobQuestions(jId);
          setQuestions(qs);
        } else if (currentJob.status === 'failed') {
          setError(currentJob.error_message || 'Quá trình sinh câu hỏi thất bại.');
        } else {
          // Keep polling
          timeoutId = window.setTimeout(checkJob, 3000);
        }
      } catch (err: any) {
        setError(err.response?.data?.detail || err.message || 'Lỗi khi tải thông tin tiến trình.');
      }
    }

    checkJob();

    return () => {
      if (timeoutId) window.clearTimeout(timeoutId);
    };
  }, [jId]);

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
        <div className="jr-card card-panel jr-centered-card">
          <CircleNotch size={48} weight="bold" className="cm-spin jr-primary-icon" />
          <h2 className="jr-title">Đang sinh câu hỏi...</h2>
          <p className="jr-subtitle">AI đang phân tích tài liệu và tạo câu hỏi. Quá trình này có thể mất vài phút.</p>
        </div>
      ) : job?.status === 'failed' ? (
        <div className="jr-card card-panel jr-centered-card">
          <XCircle size={48} weight="fill" className="jr-error-icon" />
          <h2 className="jr-title">Sinh câu hỏi thất bại</h2>
          <p className="jr-subtitle">{error}</p>
          <div className="jr-actions-center">
            <Link to={`/courses/${cId}/materials/${mId}/generate`} className="jr-btn-primary">
              Thử lại
            </Link>
            <Link to={`/courses/${cId}/materials/${mId}`} className="jr-btn-secondary">
              Quay lại tài liệu
            </Link>
          </div>
        </div>
      ) : (
        <div className="jr-results-wrapper">
          <div className="jr-header">
            <div>
              <h1 className="jr-title">Kết quả sinh câu hỏi</h1>
              <p className="jr-subtitle">
                Đã tạo thành công {questions.length} câu hỏi từ tài liệu {material?.title}.
              </p>
            </div>
            <div className="jr-header-actions">
              <Link to={`/courses/${cId}/materials/${mId}/generate`} className="jr-btn-secondary">
                Tạo thêm câu hỏi
              </Link>
            </div>
          </div>

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

              return (
              <div key={q.id} className={`jr-question-card card-panel ${allWarnings.length > 0 ? 'jr-card-has-warnings' : ''}`}>
                <div className="jr-question-header">
                  <span className="jr-question-number">Câu {index + 1}</span>
                  <div className="jr-question-badges">
                    <span className="jr-badge jr-badge-difficulty">Độ khó: {q.difficulty}</span>
                    <span className="jr-badge jr-badge-bloom">Bloom: {q.bloom_level}</span>
                    {Object.entries(llmScores).map(([key, value]) => {
                        let label = key;
                        if (key === 'grounding') label = 'Relevance';
                        if (key === 'clarity') label = 'Clarity';
                        if (key === 'assessment_quality') label = 'Correctness';
                        
                        return (
                          <span key={key} className={`jr-badge jr-badge-score ${getScoreClass(value)}`} title={`${key}: ${value}`}>
                            {label}: {formatScore(value)}
                          </span>
                        );
                    })}
                  </div>
                </div>
                
                {allWarnings.length > 0 && (
                  <div className="jr-warnings-box">
                    <div className="jr-warnings-header">
                      <WarningCircle size={18} weight="fill" />
                      <strong>Cảnh báo chất lượng ({allWarnings.length}):</strong>
                    </div>
                    <ul className="jr-warnings-list">
                      {allWarnings.map((warn, wIdx) => (
                        <li key={wIdx}>{warn}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                <p className="jr-question-content">{q.content}</p>
                
                <div className="jr-options-list">
                  {q.options.map((opt, optIndex) => (
                    <div 
                      key={opt.id} 
                      className={`jr-option-item ${opt.is_correct ? 'jr-option-correct' : ''}`}
                    >
                      <div className="jr-option-marker">
                        {String.fromCharCode(65 + optIndex)}
                      </div>
                      <div className="jr-option-text">{opt.content}</div>
                      {opt.is_correct && <CheckCircle size={20} weight="fill" className="jr-correct-icon" />}
                    </div>
                  ))}
                </div>

                {q.explanation && (
                  <div className="jr-explanation-box">
                    <div className="jr-explanation-header">
                      <Lightbulb size={18} weight="duotone" />
                      <strong>Giải thích:</strong>
                    </div>
                    <p>{q.explanation}</p>
                  </div>
                )}
                
                {q.source_chunk_ids && q.source_chunk_ids.length > 0 && (
                  <div className="jr-source-meta">
                    Tham chiếu từ các đoạn: {q.source_chunk_ids.join(', ')}
                  </div>
                )}
              </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
