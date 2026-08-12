import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { CaretRight, Sparkle, CircleNotch, ArrowLeft } from '@phosphor-icons/react';
import { getCachedCourseById, fetchCourseById, type Course } from '../services/courseApi';
import { getCachedMaterialById, getMaterialById, type MaterialDetail } from '../services/materialApi';
import { createQuestionGenerationJob, type JobConfig } from '../services/jobApi';
import './GenerateQuestions.css';

export const GenerateQuestions: React.FC = () => {
  const { courseId, materialId } = useParams<{ courseId: string; materialId: string }>();
  const navigate = useNavigate();

  const cId = Number(courseId);
  const mId = Number(materialId);

  const [course, setCourse] = useState<Course | null>(getCachedCourseById(cId));
  const [material, setMaterial] = useState<MaterialDetail | null>(getCachedMaterialById(mId));
  const [loading, setLoading] = useState(!(course && material));
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [numberOfQuestions, setNumberOfQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState('medium');
  const [bloomLevel, setBloomLevel] = useState('');
  const [language, setLanguage] = useState('vi');
  const [query, setQuery] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    async function loadData() {
      if (course && material) return;
      setLoading(true);
      try {
        const [c, m] = await Promise.all([
          fetchCourseById(cId),
          getMaterialById(mId)
        ]);
        setCourse(c);
        setMaterial(m);
      } catch {
        setError('Không thể tải thông tin khóa học hoặc tài liệu.');
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [cId, mId, course, material]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!material) return;

    setIsSubmitting(true);
    setError(null);

    const config: JobConfig = {
      number_of_questions: numberOfQuestions,
      difficulty,
      language,
      top_k: 5,
    };
    if (bloomLevel) config.bloom_level = bloomLevel;
    if (query.trim()) config.query = query.trim();

    try {
      const job = await createQuestionGenerationJob(mId, config);
      navigate(`/courses/${cId}/materials/${mId}/jobs/${job.id}`);
    } catch (err: any) {
      console.error('Lỗi khi tạo job sinh câu hỏi:', err);
      setError(err.response?.data?.detail || err.message || 'Có lỗi xảy ra khi bắt đầu sinh câu hỏi.');
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="gq-container gq-centered">
        <CircleNotch size={32} weight="bold" className="cm-spin" />
        <p>Đang tải...</p>
      </div>
    );
  }

  if (error || !course || !material) {
    return (
      <div className="gq-container gq-centered">
        <h2>Đã có lỗi xảy ra</h2>
        <p>{error || 'Không tìm thấy dữ liệu.'}</p>
        <Link to={`/courses/${cId}/materials`} className="gq-btn-back">
          <ArrowLeft size={16} /> Quay lại
        </Link>
      </div>
    );
  }

  return (
    <div className="gq-container">
      {/* Breadcrumb */}
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
            <Link to={`/courses/${cId}/materials`} className="cm-breadcrumb-link">Tài liệu</Link>
          </li>
          <li className="cm-breadcrumb-separator" aria-hidden="true"><CaretRight size={14} weight="bold" /></li>
          <li className="cm-breadcrumb-item">
            <Link to={`/courses/${cId}/materials/${mId}`} className="cm-breadcrumb-link cm-breadcrumb-course-name">{material.title}</Link>
          </li>
          <li className="cm-breadcrumb-separator" aria-hidden="true"><CaretRight size={14} weight="bold" /></li>
          <li className="cm-breadcrumb-item">
            <span aria-current="page" className="cm-breadcrumb-current">Tạo câu hỏi</span>
          </li>
        </ol>
      </nav>

      <div className="gq-card card-panel">
        <div className="gq-header">
          <div className="gq-header-icon">
            <Sparkle size={28} weight="duotone" />
          </div>
          <div>
            <h1 className="gq-title">Sinh câu hỏi trắc nghiệm</h1>
            <p className="gq-subtitle">Tạo câu hỏi tự động từ tài liệu <strong>{material.title}</strong> sử dụng AI.</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="gq-form">
          {error && (
            <div className="gq-error-alert" role="alert">
              {error}
            </div>
          )}

          <div className="gq-form-row">
            <div className="gq-form-group">
              <label htmlFor="number_of_questions">Số lượng câu hỏi</label>
              <input
                id="number_of_questions"
                type="number"
                min="1"
                max="50"
                value={numberOfQuestions}
                onChange={(e) => setNumberOfQuestions(Number(e.target.value))}
                required
              />
            </div>
            
            <div className="gq-form-group">
              <label htmlFor="difficulty">Độ khó</label>
              <select
                id="difficulty"
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="easy">Dễ</option>
                <option value="medium">Trung bình</option>
                <option value="hard">Khó</option>
              </select>
            </div>
          </div>

          <div className="gq-form-row">
            <div className="gq-form-group">
              <label htmlFor="bloomLevel">Mức độ nhận thức (Bloom)</label>
              <select
                id="bloomLevel"
                value={bloomLevel}
                onChange={(e) => setBloomLevel(e.target.value)}
              >
                <option value="">Tất cả mức độ</option>
                <option value="remember">Nhớ (Remember)</option>
                <option value="understand">Hiểu (Understand)</option>
                <option value="apply">Vận dụng (Apply)</option>
                <option value="analyze">Phân tích (Analyze)</option>
                <option value="evaluate">Đánh giá (Evaluate)</option>
                <option value="create">Sáng tạo (Create)</option>
              </select>
            </div>
            
            <div className="gq-form-group">
              <label htmlFor="language">Ngôn ngữ</label>
              <select
                id="language"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="vi">Tiếng Việt</option>
                <option value="en">Tiếng Anh</option>
              </select>
            </div>
          </div>

          <div className="gq-form-group">
            <label htmlFor="query">Yêu cầu bổ sung hoặc phạm vi sinh (Tùy chọn)</label>
            <textarea
              id="query"
              rows={3}
              placeholder="VD: Chỉ tập trung vào chương 2, hoặc sinh câu hỏi mang tính tình huống..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <span className="gq-help-text">Để trống để AI tự động trích xuất ngẫu nhiên từ toàn bộ tài liệu.</span>
          </div>

          <div className="gq-form-actions">
            <Link to={`/courses/${cId}/materials/${mId}`} className="gq-btn-cancel">
              Hủy
            </Link>
            <button
              type="submit"
              className="gq-btn-submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <CircleNotch size={18} className="cm-spin" />
                  Đang khởi tạo...
                </>
              ) : (
                <>
                  <Sparkle size={18} />
                  Bắt đầu sinh câu hỏi
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
