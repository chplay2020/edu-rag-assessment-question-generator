import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  FilePdf,
  FileDoc,
  FileText,
  File,
  DownloadSimple,
  CircleNotch,
  WarningCircle,
  ArrowLeft,
  Gear,
  CaretRight,
  CheckCircle,
  X,
  ArrowsClockwise,
} from '@phosphor-icons/react';
import { fetchCourseById, getCachedCourseById, type Course } from '../services/courseApi';
import {
  getMaterialById,
  getCachedMaterialById,
  downloadMaterialFile,
  extractApiError,
  formatViDate,
  type MaterialDetail as MaterialDetailType,
} from '../services/materialApi';
import {
  getMockState,
  mockProcessMaterial,
  resetMockState,
  type ProcessingStatus,
  type MockProcessingState,
  type MockProcessOptions,
} from '../mocks/materialProcessingMock';
import { getMaterialStatusMeta } from '../utils/materialStatus';
import './MaterialDetail.css';

// File Icon

function FileIcon({ filename, size = 20 }: { filename: string; size?: number }) {
  const ext = filename.split('.').pop()?.toLowerCase() ?? '';
  if (ext === 'pdf') return <FilePdf size={size} weight="duotone" />;
  if (ext === 'docx' || ext === 'doc') return <FileDoc size={size} weight="duotone" />;
  if (ext === 'txt') return <FileText size={size} weight="duotone" />;
  return <File size={size} weight="duotone" />;
}

// Hiển thị trạng thái Material bằng tiếng Việt, dùng helper dùng chung
function StatusBadge({ status }: { status: string }) {
  const { label, modifier } = getMaterialStatusMeta(status);
  return (
    <span className={`md-status-badge md-status-${modifier}`}>
      {label}
    </span>
  );
}

// Toast type

interface ToastState {
  type: 'success' | 'error';
  message: string;
}

// Main Component

export const MaterialDetail: React.FC = () => {
  const { courseId, materialId } = useParams<{ courseId: string; materialId: string }>();

  const cId = Number(courseId);
  const mId = Number(materialId);
  const isValidCourseId = Number.isInteger(cId) && cId > 0;
  const isValidMaterialId = Number.isInteger(mId) && mId > 0;
  const initialCourse = isValidCourseId ? getCachedCourseById(cId) : null;
  const cachedMaterial = isValidMaterialId ? getCachedMaterialById(mId) : null;
  const initialMaterial = cachedMaterial?.course_id === cId ? cachedMaterial : null;

  // API data state
  const [course, setCourse] = useState<Course | null>(initialCourse);
  const [material, setMaterial] = useState<MaterialDetailType | null>(initialMaterial);
  const [loading, setLoading] = useState(!(initialCourse && initialMaterial));
  const [error, setError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  // Mock processing state (T029)
  const [mockStatus, setMockStatus] = useState<ProcessingStatus | null>(null);
  const [mockFailureReason, setMockFailureReason] = useState<string | null>(null);
  const [mockChunkCount, setMockChunkCount] = useState<number>(0);
  const [mockPreviewText, setMockPreviewText] = useState<string | null>(null);
  const [simulateFailure, setSimulateFailure] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  // Toast
  const [toast, setToast] = useState<ToastState | null>(null);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Safety: track mount state
  const isMountedRef = useRef(true);

  // Toast helper
  const showToast = useCallback((type: 'success' | 'error', message: string) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToast({ type, message });
    toastTimerRef.current = setTimeout(() => {
      if (isMountedRef.current) setToast(null);
    }, 4500);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    };
  }, []);

  // Restore mock state on mount
  useEffect(() => {
    if (!isValidMaterialId) return;
    const existing = getMockState(mId);
    if (!existing) return;
    setMockStatus(existing.status);
    setMockFailureReason(existing.failureReason);
    if (existing.status === 'done') {
      setMockChunkCount(existing.chunkCount);
      setMockPreviewText(existing.extractedTextPreview);
    }

  }, [mId, isValidMaterialId]);

  // Poll mock state while processing
  useEffect(() => {
    if (mockStatus !== 'processing' && mockStatus !== 'pending') return;

    const interval = setInterval(() => {
      const state = getMockState(mId);
      if (!state) { clearInterval(interval); return; }

      if (state.status === 'done' || state.status === 'failed') {
        clearInterval(interval);
        if (!isMountedRef.current) return;
        setMockStatus(state.status);
        if (state.status === 'done') {
          setMockChunkCount(state.chunkCount);
          setMockPreviewText(state.extractedTextPreview);
          showToast('success', 'Tài liệu đã được xử lý thành công!');
        } else {
          setMockFailureReason(state.failureReason);
          showToast('error', 'Xử lý tài liệu thất bại!');
        }
      }
    }, 600);

    return () => clearInterval(interval);
  }, [mockStatus, mId, showToast]);

  // Load API data
  const loadData = useCallback(async () => {
    if (!isValidCourseId || !isValidMaterialId) {
      setError('Không tìm thấy tài liệu hoặc bạn không có quyền truy cập.');
      setLoading(false);
      return;
    }

    const cachedCourse = getCachedCourseById(cId);
    const currentMaterial = getCachedMaterialById(mId);
    const cachedMaterialForCourse = currentMaterial?.course_id === cId ? currentMaterial : null;
    if (cachedCourse) setCourse(cachedCourse);
    if (cachedMaterialForCourse) setMaterial(cachedMaterialForCourse);
    setLoading(!(cachedCourse && cachedMaterialForCourse));
    setError(null);

    try {
      const [courseData, materialData] = await Promise.all([
        fetchCourseById(cId),
        getMaterialById(mId),
      ]);

      if (materialData.course_id !== cId) {
        setError('Không tìm thấy tài liệu hoặc bạn không có quyền truy cập.');
      } else {
        setCourse(courseData);
        setMaterial(materialData);
      }
    } catch (err: unknown) {
      console.error('Lỗi tải dữ liệu MaterialDetail:', err);
      const anyErr = err as { response?: { status?: number } };
      const msg = extractApiError(err);
      if (anyErr?.response?.status === 404 || anyErr?.response?.status === 403) {
        setError('Không tìm thấy tài liệu hoặc bạn không có quyền truy cập.');
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  }, [cId, mId, isValidCourseId, isValidMaterialId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Download
  const handleDownloadBtn = async () => {
    if (!material || !material.file_url) return;
    setIsDownloading(true);
    setDownloadError(null);
    try {
      await downloadMaterialFile(material.file_url, material.title);
    } catch {
      setDownloadError('Lỗi khi tải file. Vui lòng thử lại sau.');
    } finally {
      setIsDownloading(false);
    }
  };

  // Mock processing handlers
  const handleProcessClick = () => {
    setShowConfirmModal(true);
  };

  const handleConfirmProcess = () => {
    setShowConfirmModal(false);
    setMockFailureReason(null);

    const opts: MockProcessOptions = { simulateFailure };

    mockProcessMaterial(mId, opts, (state: MockProcessingState) => {
      if (!isMountedRef.current) return;
      setMockStatus(state.status);
      if (state.status === 'processing') {
        showToast('success', 'Đã bắt đầu xử lý tài liệu, vui lòng chờ...');
      } else if (state.status === 'done') {
        setMockChunkCount(state.chunkCount);
        setMockPreviewText(state.extractedTextPreview);
        showToast('success', 'Tài liệu đã được xử lý thành công!');
      } else if (state.status === 'failed') {
        setMockFailureReason(state.failureReason);
        showToast('error', 'Xử lý tài liệu thất bại!');
      }
    }).catch((err: unknown) => {
      if (!isMountedRef.current) return;
      console.error('[T029 Mock] Lỗi không xác định:', err);
      setMockStatus('failed');
      setMockFailureReason('Lỗi không xác định trong môi trường mock.');
      showToast('error', 'Xử lý tài liệu thất bại!');
    });
  };

  const handleRetryProcess = () => {
    resetMockState(mId);
    setMockStatus(null);
    setMockFailureReason(null);
    setMockChunkCount(0);
    setMockPreviewText(null);
    setShowConfirmModal(true);
  };

  // Computed display values
  const isProcessingActive = mockStatus === 'pending' || mockStatus === 'processing';
  const effectiveStatus = mockStatus ?? (material?.status ?? 'unknown');
  const effectiveChunkCount = mockStatus === 'done' ? mockChunkCount : (material?.chunk_count ?? 0);
  const effectivePreview = mockStatus === 'done' ? mockPreviewText : material?.extracted_text_preview;
  const hasPreview = Boolean(effectivePreview && effectivePreview.trim().length > 0);

  // Loading
  if (loading) {
    return (
      <div className="md-container md-centered">
        <CircleNotch size={32} weight="bold" className="cm-spin" />
        <p>Đang tải thông tin tài liệu...</p>
      </div>
    );
  }

  const backUrl = isValidCourseId ? `/courses/${cId}/materials` : '/courses';

  if (error || !course || !material) {
    return (
      <div className="md-container md-centered">
        <WarningCircle size={48} weight="fill" className="md-error-icon" />
        <h2>Đã có lỗi xảy ra</h2>
        <p>{error || 'Không tìm thấy tài liệu hoặc bạn không có quyền truy cập.'}</p>
        <Link to={backUrl} className="md-btn-back">
          <ArrowLeft size={16} /> Quay lại danh sách tài liệu
        </Link>
      </div>
    );
  }

  return (
    <div className="md-container">

      {/* Toast */}
      {toast && (
        <div
          className={`md-toast md-toast-${toast.type}`}
          role="alert"
          aria-live="polite"
        >
          {toast.type === 'success'
            ? <CheckCircle size={18} weight="fill" />
            : <WarningCircle size={18} weight="fill" />
          }
          <span>{toast.message}</span>
          <button
            className="md-toast-close"
            onClick={() => setToast(null)}
            aria-label="Đóng thông báo"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Confirm Modal */}
      {showConfirmModal && (
        <div
          className="md-modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="md-modal-title"
          onClick={(e) => {
            if (e.target === e.currentTarget) setShowConfirmModal(false);
          }}
        >
          <div className="md-modal-dialog">
            <h3 id="md-modal-title" className="md-modal-title">
              Xác nhận xử lý tài liệu
            </h3>
            <p className="md-modal-body">
              Tài liệu <strong>"{material.title}"</strong> sẽ được phân tích và tách thành
              các đoạn nội dung để hỗ trợ tìm kiếm và tạo câu hỏi.
            </p>
            <label className="md-modal-toggle" htmlFor="md-simulate-failure">
              <input
                id="md-simulate-failure"
                type="checkbox"
                checked={simulateFailure}
                onChange={(e) => setSimulateFailure(e.target.checked)}
              />
              <span>[Mock] Giả lập kịch bản thất bại</span>
            </label>
            <div className="md-modal-actions">
              <button
                className="md-modal-btn-cancel"
                onClick={() => setShowConfirmModal(false)}
              >
                Huỷ
              </button>
              <button
                className="md-modal-btn-confirm"
                onClick={handleConfirmProcess}
              >
                Xác nhận xử lý
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Breadcrumb */}
      <nav className="cm-breadcrumb" aria-label="Breadcrumb" style={{ marginBottom: '16px' }}>
        <ol className="cm-breadcrumb-list">
          <li className="cm-breadcrumb-item">
            <Link to="/courses" className="cm-breadcrumb-link">Môn học</Link>
          </li>
          <li className="cm-breadcrumb-separator" aria-hidden="true">
            <CaretRight size={14} weight="bold" />
          </li>
          <li className="cm-breadcrumb-item">
            <Link to={`/courses/${cId}`} className="cm-breadcrumb-link cm-breadcrumb-course-name">
              {course.title}
            </Link>
          </li>
          <li className="cm-breadcrumb-separator" aria-hidden="true">
            <CaretRight size={14} weight="bold" />
          </li>
          <li className="cm-breadcrumb-item">
            <Link to={`/courses/${cId}/materials`} className="cm-breadcrumb-link">Tài liệu</Link>
          </li>
          <li className="cm-breadcrumb-separator" aria-hidden="true">
            <CaretRight size={14} weight="bold" />
          </li>
          <li className="cm-breadcrumb-item">
            <span aria-current="page" className="cm-breadcrumb-current">{material.title}</span>
          </li>
        </ol>
      </nav>

      {/* Header Card */}
      <div className="md-header card-panel">
        <div className="md-header-top">
          {/* Title + meta */}
          <div className="md-title-wrapper">
            <div className="md-icon-wrapper" aria-hidden="true">
              <FileIcon filename={material.title} size={28} />
            </div>
            <div className="md-title-block">
              <h1 className="md-title" title={material.title}>{material.title}</h1>
              <div className="md-inline-meta">
                <StatusBadge status={effectiveStatus} />
                <div className="md-secondary-meta">
                  <span title="Mã môn học">{course.code}</span>
                  <span className="md-meta-dot">·</span>
                  <span title="Ngày tải lên">{formatViDate(material.created_at)}</span>
                  <span className="md-meta-dot">·</span>
                  <span title="ID người tải">ID người tải: {material.uploaded_by}</span>
                  <span className="md-meta-dot">·</span>
                  <span title="Số đoạn nội dung">Số đoạn nội dung: {effectiveChunkCount}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="md-actions">
            {/* Download – unchanged */}
            <button
              className="md-btn-download"
              onClick={handleDownloadBtn}
              disabled={!material.file_url || isDownloading}
              aria-label={`Tải xuống ${material.title}`}
            >
              {isDownloading
                ? <CircleNotch size={18} className="cm-spin" />
                : <DownloadSimple size={18} />
              }
              <span>Tải xuống</span>
            </button>

            {/* Process button – pending / processing */}
            {isProcessingActive && (
              <button
                className="md-btn-process"
                disabled
                aria-disabled="true"
                aria-label="Tài liệu đang được xử lý, vui lòng chờ"
              >
                <CircleNotch size={18} className="md-spin" />
                <span>
                  {mockStatus === 'pending' ? 'Đang chuẩn bị...' : 'Đang xử lý'}
                </span>
              </button>
            )}

            {/* Process button – idle (null) or failed */}
            {!isProcessingActive && mockStatus !== 'done' && (
              <button
                className={`md-btn-process${mockStatus === 'failed' ? ' md-btn-process-retry' : ''}`}
                onClick={mockStatus === 'failed' ? handleRetryProcess : handleProcessClick}
                aria-label={
                  mockStatus === 'failed'
                    ? 'Thử lại xử lý tài liệu'
                    : 'Xử lý tài liệu'
                }
              >
                {mockStatus === 'failed'
                  ? <ArrowsClockwise size={18} />
                  : <Gear size={18} />
                }
                <span>{mockStatus === 'failed' ? 'Thử lại' : 'Xử lý tài liệu'}</span>
              </button>
            )}

            {/* Process button – done */}
            {mockStatus === 'done' && (
              <button
                className="md-btn-process md-btn-process-done"
                disabled
                aria-disabled="true"
                aria-label="Tài liệu đã được xử lý"
              >
                <CheckCircle size={18} />
                <span>Đã xử lý</span>
              </button>
            )}
          </div>
        </div>

        {/* Download error */}
        {downloadError && (
          <div className="md-error-message" role="alert">
            <WarningCircle size={16} /> {downloadError}
          </div>
        )}

        {/* Process failure reason */}
        {mockStatus === 'failed' && mockFailureReason && (
          <div className="md-process-error" role="alert">
            <WarningCircle size={16} weight="fill" />
            <span className="md-process-error-body">{mockFailureReason}</span>
            <button
              className="md-process-error-dismiss"
              onClick={() => setMockFailureReason(null)}
              aria-label="Đóng thông báo lỗi"
            >
              <X size={14} />
            </button>
          </div>
        )}
      </div>

      {/* Preview Section */}
      <div className="md-preview-section card-panel">
        <h3 className="md-preview-title">Xem trước nội dung</h3>

        {/* Processing spinner */}
        {isProcessingActive && (
          <div className="md-preview-processing" aria-live="polite" aria-label="Đang xử lý tài liệu">
            <CircleNotch size={28} className="md-spin" />
            <p>
              {mockStatus === 'pending'
                ? 'Đang chuẩn bị xử lý tài liệu...'
                : 'Đang phân tích và tách nội dung, vui lòng chờ...'
              }
            </p>
          </div>
        )}

        {/* Preview content */}
        {!isProcessingActive && hasPreview && (
          <div className="md-preview-content">
            {effectivePreview}
          </div>
        )}

        {/* Empty state */}
        {!isProcessingActive && !hasPreview && (
          <div className="md-preview-empty">
            <FileText size={40} weight="duotone" className="md-empty-icon" aria-hidden="true" />
            <p className="md-empty-title">Chưa có nội dung.</p>
            <p className="md-empty-desc">
              {mockStatus === 'failed'
                ? 'Xử lý thất bại. Vui lòng thử lại.'
                : 'Nội dung sẽ xuất hiện sau khi tài liệu được xử lý.'
              }
            </p>
          </div>
        )}
      </div>

      <div className="md-footer-actions">
        <Link to={`/courses/${cId}/materials`} className="md-btn-back-outline">
          <ArrowLeft size={16} /> Quay lại danh sách tài liệu
        </Link>
      </div>
    </div>
  );
};
