import React, { useEffect, useState, useCallback } from 'react';
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
  CaretRight
} from '@phosphor-icons/react';
import { fetchCourseById, getCachedCourseById, type Course } from '../services/courseApi';
import {
  getMaterialById,
  getCachedMaterialById,
  downloadMaterialFile,
  extractApiError,
  formatViDate,
  type MaterialDetail as MaterialDetailType
} from '../services/materialApi';
import './MaterialDetail.css';

function FileIcon({ filename, size = 20 }: { filename: string; size?: number }) {
  const ext = filename.split('.').pop()?.toLowerCase() ?? '';
  if (ext === 'pdf') return <FilePdf size={size} weight="duotone" />;
  if (ext === 'docx' || ext === 'doc') return <FileDoc size={size} weight="duotone" />;
  if (ext === 'txt') return <FileText size={size} weight="duotone" />;
  return <File size={size} weight="duotone" />;
}

function StatusBadge({ status }: { status: string }) {
  const labelMap: Record<string, string> = {
    processing: 'Đang xử lý',
    ready: 'Sẵn sàng',
    error: 'Xử lý thất bại',
    pending: 'Đang chờ',
    done: 'Đã xử lý',
    completed: 'Đã xử lý',
    failed: 'Xử lý thất bại'
  };
  const label = labelMap[status] ?? 'Chưa xác định';

  let badgeClass = 'md-status-unknown';
  if (status === 'processing' || status === 'pending') badgeClass = 'md-status-processing';
  else if (status === 'ready' || status === 'done' || status === 'completed') badgeClass = 'md-status-ready';
  else if (status === 'error' || status === 'failed') badgeClass = 'md-status-error';

  return <span className={`md-status-badge ${badgeClass}`}>{label}</span>;
}

export const MaterialDetail: React.FC = () => {
  const { courseId, materialId } = useParams<{ courseId: string; materialId: string }>();

  const cId = Number(courseId);
  const mId = Number(materialId);
  const isValidCourseId = Number.isInteger(cId) && cId > 0;
  const isValidMaterialId = Number.isInteger(mId) && mId > 0;
  const initialCourse = isValidCourseId ? getCachedCourseById(cId) : null;
  const cachedMaterial = isValidMaterialId ? getCachedMaterialById(mId) : null;
  const initialMaterial = cachedMaterial?.course_id === cId ? cachedMaterial : null;

  const [course, setCourse] = useState<Course | null>(initialCourse);
  const [material, setMaterial] = useState<MaterialDetailType | null>(initialMaterial);
  const [loading, setLoading] = useState(!(initialCourse && initialMaterial));
  const [error, setError] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

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
        getMaterialById(mId)
      ]);

      if (materialData.course_id !== cId) {
        setError('Không tìm thấy tài liệu hoặc bạn không có quyền truy cập.');
      } else {
        setCourse(courseData);
        setMaterial(materialData);
      }
    } catch (err: any) {
      console.error('Lỗi tải dữ liệu MaterialDetail:', err);
      const msg = extractApiError(err);
      if (err?.response?.status === 404 || err?.response?.status === 403) {
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

  if (loading) {
    return (
      <div className="md-container md-centered">
        <CircleNotch size={32} weight="bold" className="cm-spin" />
        <p>Đang tải thông tin tài liệu...</p>
      </div>
    );
  }

  const backUrl = isValidCourseId
    ? `/courses/${cId}/materials`
    : '/courses';

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

  const hasPreview = material.extracted_text_preview && material.extracted_text_preview.trim().length > 0;

  return (
    <div className="md-container">
      {/* Breadcrumb */}
      <nav className="cm-breadcrumb" aria-label="Breadcrumb" style={{ marginBottom: '16px' }}>
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
            <span aria-current="page" className="cm-breadcrumb-current">{material.title}</span>
          </li>
        </ol>
      </nav>

      {/* Header */}
      <div className="md-header card-panel">
        <div className="md-header-top">
          <div className="md-title-wrapper">
            <div className="md-icon-wrapper" aria-hidden="true">
              <FileIcon filename={material.title} size={28} />
            </div>
            <div className="md-title-block">
              <h1 className="md-title" title={material.title}>{material.title}</h1>
              <div className="md-inline-meta">
                <StatusBadge status={material.status} />
                <div className="md-secondary-meta">
                  <span title="Mã môn học">{course.code}</span>
                  <span className="md-meta-dot">·</span>
                  <span title="Ngày tải lên">{formatViDate(material.created_at)}</span>
                  <span className="md-meta-dot">·</span>
                  <span title="ID người tải">ID người tải: {material.uploaded_by}</span>
                  <span className="md-meta-dot">·</span>
                  <span title="Số đoạn nội dung">Số đoạn nội dung: {material.chunk_count}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="md-actions">
            <button
              className="md-btn-download"
              onClick={handleDownloadBtn}
              disabled={!material.file_url || isDownloading}
              aria-label={`Tải xuống ${material.title}`}
            >
              {isDownloading ? <CircleNotch size={18} className="cm-spin" /> : <DownloadSimple size={18} />}
              <span>Tải xuống</span>
            </button>
            <div className="md-tooltip-wrapper" title="Chức năng xử lý sẽ khả dụng sau khi Process API hoàn thành.">
              <button
                className="md-btn-process"
                disabled
                aria-disabled="true"
              >
                <Gear size={18} />
                <span>Xử lý tài liệu</span>
              </button>

            </div>
          </div>
        </div>
        {downloadError && (
          <div className="md-error-message" role="alert">
            <WarningCircle size={16} /> {downloadError}
          </div>
        )}
      </div>

      {/* Preview Section */}
      <div className="md-preview-section card-panel">
        <h3 className="md-preview-title">Xem trước nội dung</h3>
        {hasPreview ? (
          <div className="md-preview-content">
            {material.extracted_text_preview}
          </div>
        ) : (
          <div className="md-preview-empty">
            <FileText size={40} weight="duotone" className="md-empty-icon" aria-hidden="true" />
            <p className="md-empty-title">Chưa có nội dung.</p>
            <p className="md-empty-desc">Nội dung sẽ xuất hiện sau khi tài liệu được xử lý.</p>
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
