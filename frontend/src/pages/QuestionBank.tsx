import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';
import {
  CheckCircle,
  MagnifyingGlass,
  Export,
  Lightbulb,
  CaretDown,
  CircleNotch,
  WarningCircle,
  ArrowLeft,
  X,
} from '@phosphor-icons/react';
import { getQuestionBank } from '../services/questionBankApi';
import { fetchCourses, type Course } from '../services/courseApi';
import { exportExcel, formatApiErrorDetail } from '../services/exportApi';
import type { QuestionResponse } from '../services/jobApi';
import filterIcon from '../assets/filter_icon.png';
import './QuestionBank.css';

// Mapping helpers

const difficultyMap: Record<string, string> = {
  easy: 'Dễ',
  medium: 'Trung bình',
  hard: 'Khó',
};

const bloomMap: Record<string, string> = {
  remember: 'Nhớ',
  understand: 'Hiểu',
  apply: 'Vận dụng',
  analyze: 'Phân tích',
  evaluate: 'Đánh giá',
  create: 'Sáng tạo',
};

const isEnglishContent = (text: string) => {
  if (!text) return false;
  const viDiacritics = /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/i;
  return !viDiacritics.test(text);
};

// Component

interface ToastState {
  type: 'success' | 'error';
  message: string;
}

export const QuestionBank: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Filter state 
  const [courseId, setCourseId] = useState<string>(searchParams.get('course_id') ?? '');
  const [difficulty, setDifficulty] = useState('');
  const [bloomLevel, setBloomLevel] = useState('');
  const [questionType, setQuestionType] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  // Data
  const [questions, setQuestions] = useState<QuestionResponse[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Export State
  const [isExporting, setIsExporting] = useState(false);
  const exportInFlightRef = useRef(false);

  // Toast State
  const [toast, setToast] = useState<ToastState | null>(null);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showToast = useCallback((type: 'success' | 'error', message: string) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToast({ type, message });
    toastTimerRef.current = setTimeout(() => {
      setToast(null);
    }, 4000);
  }, []);

  // Selection
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());

  // Load courses for filter dropdown
  useEffect(() => {
    fetchCourses()
      .then(setCourses)
      .catch(() => {/* non-critical */ });
  }, []);

  // Fetch question bank
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setSelectedIds(new Set());
    try {
      const params: Record<string, string | number> = {};
      if (courseId) params.course_id = Number(courseId);
      if (difficulty) params.difficulty = difficulty;
      if (bloomLevel) params.bloom_level = bloomLevel;
      if (questionType) params.question_type = questionType;
      params.limit = 200;

      const data = await getQuestionBank(params as any);
      setQuestions(data);
    } catch (err: any) {
      console.error('[T058] getQuestionBank failed:', err);
      setError(err?.response?.data?.detail ?? 'Không thể tải ngân hàng câu hỏi. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  }, [courseId, difficulty, bloomLevel, questionType]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Sync courseId to URL
  useEffect(() => {
    if (courseId) {
      setSearchParams({ course_id: courseId }, { replace: true });
    } else {
      setSearchParams({}, { replace: true });
    }
  }, [courseId, setSearchParams]);

  // Client-side search filter
  const filteredQuestions = useMemo(() => {
    if (!searchQuery.trim()) return questions;
    const q = searchQuery.toLowerCase();
    return questions.filter((item) => item.content.toLowerCase().includes(q));
  }, [questions, searchQuery]);

  // Selection helpers
  const allVisibleSelected = filteredQuestions.length > 0
    && filteredQuestions.every((q) => selectedIds.has(q.id));

  const someSelected = selectedIds.size > 0;

  const toggleSelectAll = () => {
    if (allVisibleSelected) {
      const next = new Set(selectedIds);
      filteredQuestions.forEach((q) => next.delete(q.id));
      setSelectedIds(next);
    } else {
      const next = new Set(selectedIds);
      filteredQuestions.forEach((q) => next.add(q.id));
      setSelectedIds(next);
    }
  };

  const toggleSelect = (id: number) => {
    const next = new Set(selectedIds);
    if (next.has(id)) next.delete(id); else next.add(id);
    setSelectedIds(next);
  };

  const handleExportExcel = async () => {
    if (exportInFlightRef.current || selectedIds.size === 0) return;

    let objectUrl: string | null = null;
    let downloadAnchor: HTMLAnchorElement | null = null;
    let anchorAppended = false;

    try {
      exportInFlightRef.current = true;
      setIsExporting(true);

      const { blob, filename } = await exportExcel(Array.from(selectedIds));

      if (!(blob instanceof Blob) || blob.size === 0) {
        throw new Error('File rỗng hoặc dữ liệu trả về không hợp lệ.');
      }

      const type = blob.type.toLowerCase();
      if (type.includes('application/json') || type.startsWith('text/')) {
        throw new Error('Dữ liệu trả về bị lỗi (định dạng không phải là file tải xuống).');
      }

      objectUrl = URL.createObjectURL(blob);
      downloadAnchor = document.createElement('a');
      downloadAnchor.href = objectUrl;
      downloadAnchor.download = filename;
      downloadAnchor.style.display = 'none';

      document.body.appendChild(downloadAnchor);
      anchorAppended = true;
      downloadAnchor.click();

      showToast('success', 'Xuất file Excel thành công.');
      setSelectedIds(new Set());
    } catch (err: unknown) {
      let errMsg = 'Không thể xuất file Excel. Vui lòng thử lại.';
      if (axios.isAxiosError(err)) {
        const status = err.response?.status;
        if (status === 401 || status === 403) {
          errMsg = 'Hết phiên đăng nhập hoặc bạn không có quyền thao tác.';
        } else if (status === 500) {
          errMsg = 'Lỗi hệ thống khi tạo file. Vui lòng thử lại sau.';
        } else if (err.response?.data instanceof Blob) {
          try {
            const text = await err.response.data.text();
            const json = JSON.parse(text);
            errMsg = formatApiErrorDetail(json.detail);
          } catch {
            // fallback
          }
        }
      } else if (err instanceof Error) {
        errMsg = err.message;
      }
      showToast('error', errMsg);
    } finally {
      if (anchorAppended && downloadAnchor && document.body.contains(downloadAnchor)) {
        document.body.removeChild(downloadAnchor);
      }
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
      exportInFlightRef.current = false;
      setIsExporting(false);
    }
  };

  // Render
  const selectedCourse = courses.find((c) => String(c.id) === courseId);

  return (
    <div className="qb-container">
      {/* Header */}
      <div className="qb-page-header">
        <div>
          <h1 className="qb-title">Ngân hàng câu hỏi</h1>
          <p className="qb-subtitle">
            {selectedCourse
              ? <>Câu hỏi đã duyệt của môn <strong>{selectedCourse.title}</strong></>
              : 'Tất cả câu hỏi đã được duyệt'}
          </p>
        </div>
        <div className="qb-header-actions">
          {/* Export button */}
          <button
            className="qb-btn-export"
            disabled={!someSelected || isExporting}
            id="btn-export-excel"
            aria-busy={isExporting}
            onClick={handleExportExcel}
          >
            {isExporting ? <CircleNotch size={16} className="cm-spin" /> : <Export size={16} />}
            {isExporting ? 'Đang xuất...' : 'Xuất Excel'}
            {!isExporting && someSelected && <span className="qb-export-badge">{selectedIds.size}</span>}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="qb-filters">
        {/* Search */}
        <div className="qb-search-wrapper">
          <MagnifyingGlass size={16} className="qb-search-icon" />
          <input
            id="qb-search"
            type="text"
            className="qb-search-input"
            placeholder="Tìm theo nội dung câu hỏi..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button
              className="qb-search-clear"
              onClick={() => setSearchQuery('')}
              title="Xóa tìm kiếm"
            >
              <X size={14} weight="bold" />
            </button>
          )}
        </div>

        <div className="qb-filter-row">
          <img src={filterIcon} alt="Filter" className="qb-filter-icon" width={22} height={22} style={{ opacity: 0.6 }} />

          {/* Course filter */}
          <div className="jr-select-wrapper">
            <select
              id="qb-filter-course"
              className="jr-form-select qb-filter-select"
              value={courseId}
              onChange={(e) => setCourseId(e.target.value)}
            >
              <option value="">Tất cả môn học</option>
              {courses.map((c) => (
                <option key={c.id} value={String(c.id)}>{c.title}</option>
              ))}
            </select>
            <CaretDown size={13} className="jr-select-icon" />
          </div>

          {/* Difficulty filter */}
          <div className="jr-select-wrapper">
            <select
              id="qb-filter-difficulty"
              className="jr-form-select qb-filter-select"
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
            >
              <option value="">Tất cả độ khó</option>
              <option value="easy">Dễ</option>
              <option value="medium">Trung bình</option>
              <option value="hard">Khó</option>
            </select>
            <CaretDown size={13} className="jr-select-icon" />
          </div>

          {/* Bloom filter */}
          <div className="jr-select-wrapper">
            <select
              id="qb-filter-bloom"
              className="jr-form-select qb-filter-select"
              value={bloomLevel}
              onChange={(e) => setBloomLevel(e.target.value)}
            >
              <option value="">Tất cả Bloom</option>
              <option value="remember">Nhớ</option>
              <option value="understand">Hiểu</option>
              <option value="apply">Vận dụng</option>
              <option value="analyze">Phân tích</option>
              <option value="evaluate">Đánh giá</option>
              <option value="create">Sáng tạo</option>
            </select>
            <CaretDown size={13} className="jr-select-icon" />
          </div>

          {/* Question type filter */}
          <div className="jr-select-wrapper">
            <select
              id="qb-filter-type"
              className="jr-form-select qb-filter-select"
              value={questionType}
              onChange={(e) => setQuestionType(e.target.value)}
            >
              <option value="">Tất cả loại</option>
              <option value="multiple_choice">Trắc nghiệm</option>
            </select>
            <CaretDown size={13} className="jr-select-icon" />
          </div>
        </div>
      </div>

      {/* Toolbar: select-all + count */}
      {!loading && !error && filteredQuestions.length > 0 && (
        <div className="qb-toolbar">
          <label className="qb-select-all-label" htmlFor="qb-select-all">
            <input
              id="qb-select-all"
              type="checkbox"
              className="qb-checkbox"
              checked={allVisibleSelected}
              onChange={toggleSelectAll}
            />
            Chọn tất cả ({filteredQuestions.length} câu)
          </label>
          {someSelected && (
            <span className="qb-selected-info">
              Đã chọn <strong>{selectedIds.size}</strong> câu
            </span>
          )}
        </div>
      )}

      {/* States */}
      {loading && (
        <div className="jr-state-card">
          <CircleNotch size={40} weight="bold" className="cm-spin jr-primary-icon" />
          <p>Đang tải câu hỏi...</p>
        </div>
      )}

      {!loading && error && (
        <div className="jr-state-card">
          <WarningCircle size={40} weight="fill" className="jr-error-icon" />
          <p className="jr-subtitle">{error}</p>
          <button className="jr-btn-primary" onClick={fetchData}>Thử lại</button>
        </div>
      )}

      {!loading && !error && filteredQuestions.length === 0 && (
        <div className="jr-state-card">
          <CheckCircle size={40} weight="duotone" style={{ color: 'var(--color-text-muted)', marginBottom: 12 }} />
          <p className="jr-subtitle">
            {searchQuery
              ? `Không tìm thấy câu hỏi nào khớp với "${searchQuery}".`
              : 'Chưa có câu hỏi nào được duyệt trong bộ lọc hiện tại.'}
          </p>
          {courseId && (
            <Link to="/question-bank" className="jr-btn-secondary">Xem tất cả môn học</Link>
          )}
        </div>
      )}

      {/* Question list */}
      {!loading && !error && filteredQuestions.length > 0 && (
        <div className="jr-question-list">
          {filteredQuestions.map((q, index) => {
            const isEn = isEnglishContent(q.content);
            const isSelected = selectedIds.has(q.id);

            return (
              <div
                key={q.id}
                className={`jr-question-card qb-question-card ${isSelected ? 'qb-card-selected' : ''}`}
              >
                {/* Card header */}
                <div className="jr-question-header">
                  <div className="qb-card-left">
                    <label className="qb-checkbox-label" htmlFor={`qb-check-${q.id}`}>
                      <input
                        id={`qb-check-${q.id}`}
                        type="checkbox"
                        className="qb-checkbox"
                        checked={isSelected}
                        onChange={() => toggleSelect(q.id)}
                      />
                    </label>
                    <span className="jr-question-number">
                      {isEn ? `Question ${index + 1}` : `Câu ${index + 1}`}
                    </span>
                  </div>
                  <div className="jr-question-badges">
                    <span className="jr-badge jr-badge-difficulty">
                      {isEn ? 'Difficulty:' : 'Độ khó:'}{' '}
                      {isEn
                        ? q.difficulty.charAt(0).toUpperCase() + q.difficulty.slice(1)
                        : difficultyMap[q.difficulty] ?? q.difficulty}
                    </span>
                    <span className="jr-badge jr-badge-bloom">
                      Bloom:{' '}
                      {isEn
                        ? q.bloom_level.charAt(0).toUpperCase() + q.bloom_level.slice(1)
                        : bloomMap[q.bloom_level] ?? q.bloom_level}
                    </span>
                  </div>
                </div>

                {/* Question body */}
                <div className="jr-question-body">
                  <p className="jr-question-content">{q.content}</p>
                  <div className="jr-options-list">
                    {q.options.map((opt, optIdx) => (
                      <div
                        key={opt.id}
                        className={`jr-option-item ${opt.is_correct ? 'jr-option-correct' : ''}`}
                      >
                        <div className="jr-option-marker">{String.fromCharCode(65 + optIdx)}</div>
                        <div className="jr-option-text">{opt.content}</div>
                        {opt.is_correct && (
                          <CheckCircle size={18} weight="fill" className="jr-correct-icon" />
                        )}
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
              </div>
            );
          })}
        </div>
      )}

      {/* Back link */}
      {!loading && (
        <div style={{ marginTop: '24px' }}>
          <Link to="/courses" className="jr-btn-back">
            <ArrowLeft size={16} /> Quay lại danh sách môn học
          </Link>
        </div>
      )}

      {/* Toast notification */}
      {toast && (
        <div className={`md-toast md-toast-${toast.type}`} role="alert" aria-live="polite">
          {toast.type === 'success'
            ? <CheckCircle size={20} weight="fill" className="md-toast-icon" />
            : <WarningCircle size={20} weight="fill" className="md-toast-icon" />
          }
          <span>{toast.message}</span>
          <button
            className="md-toast-close"
            onClick={() => setToast(null)}
          >
            <X size={16} />
          </button>
        </div>
      )}
    </div>
  );
};
