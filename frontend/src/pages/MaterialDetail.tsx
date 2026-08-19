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
  Sparkle,
} from '@phosphor-icons/react';
import { useNavigate } from 'react-router-dom';
import { fetchCourseById, getCachedCourseById, type Course } from '../services/courseApi';
import {
  getMaterialById,
  getCachedMaterialById,
  downloadMaterialFile,
  processMaterial,
  getJobById,
  extractApiError,
  formatViDate,
  type MaterialDetail as MaterialDetailType,
} from '../services/materialApi';
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

// Status Badge

function StatusBadge({ status }: { status: string }) {
  const { label, modifier } = getMaterialStatusMeta(status);
  return (
    <span className={`md-status-badge md-status-${modifier}`}>
      {label}
    </span>
  );
}

// Toast

interface ToastState {
  type: 'success' | 'error';
  message: string;
}

// Processing State

type ProcessPhase =
  | 'idle'
  | 'sending'
  | 'polling'
  | 'done'
  | 'failed';

// Main Component

export const MaterialDetail: React.FC = () => {
  const { courseId, materialId } = useParams<{ courseId: string; materialId: string }>();
  const navigate = useNavigate();

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

  //  Processing / polling state
  const [processPhase, setProcessPhase] = useState<ProcessPhase>('idle');
  const [jobStatus, setJobStatus] = useState<string | null>(null);
  const [processError, setProcessError] = useState<string | null>(null);


  // Toast
  const [toast, setToast] = useState<ToastState | null>(null);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  //  Refs cho cleanup
  const isMountedRef = useRef(true);
  const pollingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Helpers

  const showToast = useCallback((type: 'success' | 'error', message: string) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToast({ type, message });
    toastTimerRef.current = setTimeout(() => {
      if (isMountedRef.current) setToast(null);
    }, 4500);
  }, []);

  const stopPolling = useCallback(() => {
    if (pollingTimerRef.current) {
      clearTimeout(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }
  }, []);

  // Cleanup on unmount / khi đổi materialId

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      stopPolling();
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    };
  }, [stopPolling]);

  // Reset processing state khi đổi materialId
  useEffect(() => {
    setProcessPhase('idle');
    setJobStatus(null);
    setProcessError(null);
    stopPolling();
  }, [mId, stopPolling]);

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

      if (!isMountedRef.current) return;

      if (materialData.course_id !== cId) {
        setError('Không tìm thấy tài liệu hoặc bạn không có quyền truy cập.');
      } else {
        setCourse(courseData);
        setMaterial(materialData);
      }
    } catch (err: unknown) {
      if (!isMountedRef.current) return;
      console.error('Lỗi tải dữ liệu MaterialDetail:', err);
      const anyErr = err as { response?: { status?: number } };
      if (anyErr?.response?.status === 404 || anyErr?.response?.status === 403) {
        setError('Không tìm thấy tài liệu hoặc bạn không có quyền truy cập.');
      } else {
        setError(extractApiError(err));
      }
    } finally {
      if (isMountedRef.current) setLoading(false);
    }
  }, [cId, mId, isValidCourseId, isValidMaterialId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  //  Refresh material detail

  const refreshMaterial = useCallback(async () => {
    try {
      const materialData = await getMaterialById(mId);
      if (isMountedRef.current) setMaterial(materialData);
    } catch (err) {
      console.error('[T029] Lỗi refresh material:', err);
    }
  }, [mId]);

  // Polling job status

  const scheduleNextPoll = useCallback((currentJobId: number) => {
    stopPolling();
    pollingTimerRef.current = setTimeout(async () => {
      if (!isMountedRef.current) return;

      try {
        const job = await getJobById(currentJobId);
        if (!isMountedRef.current) return;

        setJobStatus(job.status);

        if (job.status === 'done') {
          setProcessPhase('done');
          await refreshMaterial();
          if (isMountedRef.current) {
            showToast('success', 'Tài liệu đã được xử lý thành công!');
          }
        } else if (job.status === 'failed') {
          setProcessPhase('failed');
          setProcessError('Xử lý tài liệu thất bại. Vui lòng thử lại.');
          showToast('error', 'Xử lý tài liệu thất bại!');
        } else {
          // pending | running → tiếp tục poll
          scheduleNextPoll(currentJobId);
        }
      } catch (err) {
        if (!isMountedRef.current) return;
        console.error('[T029] Lỗi polling job:', err);
        // Lỗi mạng tạm thời → thử lại
        scheduleNextPoll(currentJobId);
      }
    }, 2000);
  }, [stopPolling, refreshMaterial, showToast]);

  //  Xử lý khi nhấn nút "Xử lý tài liệu"

  const handleProcessClick = useCallback(async () => {
    if (!material) return;
    setProcessPhase('sending');
    setProcessError(null);

    try {
      const resp = await processMaterial(mId);

      if (!isMountedRef.current) return;

      setJobStatus(resp.job_status);
      setProcessPhase('polling');

      // Cập nhật material status ngay lập tức (không cần reload)
      setMaterial((prev) => prev ? { ...prev, status: 'processing' } : prev);
      showToast('success', 'Đã gửi yêu cầu xử lý, đang chờ kết quả...');
      scheduleNextPoll(resp.job_id);
    } catch (err: unknown) {
      if (!isMountedRef.current) return;
      const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
      const status = axiosErr?.response?.status;

      if (status === 409) {
        const detail = axiosErr?.response?.data?.detail ?? '';
        setMaterial((prev) => prev ? { ...prev, status: 'processing' } : prev);
        setProcessPhase('polling');
        showToast('error', 'Tài liệu đang được xử lý. Không thể tạo thêm yêu cầu mới.');
        console.warn('[T029] 409 Conflict:', detail);
      } else if (status === 404) {
        setProcessPhase('idle');
        setProcessError('Không tìm thấy tài liệu hoặc bạn không có quyền truy cập.');
        showToast('error', 'Không tìm thấy tài liệu hoặc bạn không có quyền truy cập.');
      } else {
        setProcessPhase('failed');
        const msg = extractApiError(err);
        setProcessError(msg);
        showToast('error', msg);
      }
    }
  }, [material, mId, showToast, scheduleNextPoll]);

  //  Thử lại sau khi thất bại

  const handleRetryClick = useCallback(() => {
    setProcessPhase('idle');
    setJobStatus(null);
    setProcessError(null);
    stopPolling();

    setMaterial((prev) => prev ? { ...prev, status: 'failed' } : prev);
  }, [stopPolling]);

  //  Download

  const handleDownloadBtn = async () => {
    if (!material?.file_url) return;
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

  //  Computed display values
  const effectiveMaterialStatus = (() => {
    if (processPhase === 'polling' || processPhase === 'sending') return 'processing';
    if (processPhase === 'done') return material?.status ?? 'processed';
    if (processPhase === 'failed') return 'failed';
    return material?.status ?? 'unknown';
  })();

  const isProcessingActive =
    processPhase === 'sending' ||
    processPhase === 'polling' ||
    effectiveMaterialStatus === 'processing';

  // Nút có thể nhấn khi: material uploaded / failed VÀ không đang xử lý
  const canProcess =
    !isProcessingActive &&
    processPhase !== 'done' &&
    (effectiveMaterialStatus === 'uploaded' || effectiveMaterialStatus === 'failed');

  const isDone =
    processPhase === 'done' ||
    (processPhase === 'idle' && effectiveMaterialStatus === 'processed');

  const isFailed =
    processPhase === 'failed' ||
    (processPhase === 'idle' && effectiveMaterialStatus === 'failed');

  const hasPreview = Boolean(
    material?.extracted_text_preview &&
    material.extracted_text_preview.trim().length > 0
  );

  //  Loading

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

  // Render

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
                <StatusBadge status={effectiveMaterialStatus} />
                <div className="md-secondary-meta">
                  <span title="Mã môn học">{course.code}</span>
                  <span className="md-meta-dot">·</span>
                  <span title="Ngày tải lên">{formatViDate(material.created_at)}</span>
                  <span className="md-meta-dot">·</span>
                  <span title="ID người tải">ID người tải: {material.uploaded_by}</span>
                  <span className="md-meta-dot">·</span>
                  <span title="Số đoạn nội dung">Số đoạn nội dung: {material.chunk_count ?? 0}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="md-actions">
            {/* Download */}
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

            {/* Nút đang xử lý */}
            {isProcessingActive && (
              <button
                className="md-btn-process"
                disabled
                aria-disabled="true"
                aria-label="Tài liệu đang được xử lý, vui lòng chờ"
              >
                <CircleNotch size={18} className="md-spin" />
                <span>
                  {processPhase === 'sending'
                    ? 'Đang gửi yêu cầu...'
                    : jobStatus === 'pending'
                      ? 'Đang chờ xử lý...'
                      : 'Đang xử lý'}
                </span>
              </button>
            )}

            {/* Nút xử lý (uploaded / failed ở idle) */}
            {canProcess && (
              <button
                className={`md-btn-process${isFailed ? ' md-btn-process-retry' : ''}`}
                onClick={isFailed ? handleRetryClick : handleProcessClick}
                aria-label={isFailed ? 'Thử lại xử lý tài liệu' : 'Xử lý tài liệu'}
              >
                {isFailed
                  ? <ArrowsClockwise size={18} />
                  : <Gear size={18} />
                }
                <span>{isFailed ? 'Thử lại' : 'Xử lý tài liệu'}</span>
              </button>
            )}

            {/* Nút sau khi xử lý xong */}
            {isDone && !isProcessingActive && !canProcess && (
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

            {material.status === 'processed' || material.status === 'ready' || material.status === 'done' || material.status === 'completed' ? (
              <button
                className="md-btn-process"
                onClick={() => navigate(`/courses/${cId}/materials/${mId}/generate`)}
                title="Tạo câu hỏi từ tài liệu này"
              >
                <Sparkle size={18} />
                <span>Tạo câu hỏi</span>
              </button>
            ) : (
              <div className="md-tooltip-wrapper" title="Chức năng xử lý sẽ khả dụng sau khi tài liệu sẵn sàng.">
                <button
                  className="md-btn-process"
                  disabled
                  aria-disabled="true"
                >
                  <Gear size={18} />
                  <span>Xử lý tài liệu</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Download error */}
        {downloadError && (
          <div className="md-error-message" role="alert">
            <WarningCircle size={16} /> {downloadError}
          </div>
        )}

        {/* Process error */}
        {processError && (
          <div className="md-process-error" role="alert" aria-live="assertive">
            <WarningCircle size={16} weight="fill" />
            <span className="md-process-error-body">{processError}</span>
            <button
              className="md-process-error-dismiss"
              onClick={() => setProcessError(null)}
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

        {/* Đang xử lý */}
        {isProcessingActive && (
          <div
            className="md-preview-processing"
            aria-live="polite"
            aria-label="Đang xử lý tài liệu"
          >
            <CircleNotch size={28} className="md-spin" />
            <p>
              {processPhase === 'sending' || jobStatus === 'pending'
                ? 'Đang chuẩn bị xử lý tài liệu...'
                : 'Đang phân tích và tách nội dung, vui lòng chờ...'}
            </p>
          </div>
        )}

        {/* Có preview */}
        {!isProcessingActive && hasPreview && (
          <div className="md-preview-content">
            {material.extracted_text_preview}
          </div>
        )}

        {/* Empty state */}
        {!isProcessingActive && !hasPreview && (
          <div className="md-preview-empty">
            <FileText size={40} weight="duotone" className="md-empty-icon" aria-hidden="true" />
            <p className="md-empty-title">Chưa có nội dung.</p>
            <p className="md-empty-desc">
              {effectiveMaterialStatus === 'failed'
                ? 'Không thể xử lý nội dung tài liệu. Vui lòng thử lại.'
                : effectiveMaterialStatus === 'processed'
                  ? 'Nội dung đang được trích xuất.'
                  : 'Hãy xử lý tài liệu để xem trước nội dung.'}
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
