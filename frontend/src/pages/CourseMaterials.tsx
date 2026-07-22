import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  UploadSimple,
  X,
  FilePdf,
  FileDoc,
  FileText,
  File,
  DownloadSimple,
  CircleNotch,
  CheckCircle,
  WarningCircle,
  FolderDashed,
  BookOpen,
  ArrowLeft,
  CaretRight,
} from '@phosphor-icons/react';
import { fetchCourseById, getCachedCourseById, type Course } from '../services/courseApi';
import {
  uploadMaterial,
  getMaterialsByCourse,
  getCachedMaterialsByCourse,
  validateFile,
  downloadMaterialFile,
  extractApiError,
  formatViDate,
  formatFileSize,
  type Material,
  ALLOWED_EXTENSIONS,
  MAX_FILE_SIZE_MB,
} from '../services/materialApi';
import './CourseMaterials.css';

// Toast

interface ToastState {
  type: 'success' | 'error';
  message: string;
}

// icon file

function FileIcon({ filename, size = 20 }: { filename: string; size?: number }) {
  const ext = filename.split('.').pop()?.toLowerCase() ?? '';
  if (ext === 'pdf') return <FilePdf size={size} weight="duotone" />;
  if (ext === 'docx' || ext === 'doc') return <FileDoc size={size} weight="duotone" />;
  if (ext === 'txt') return <FileText size={size} weight="duotone" />;
  return <File size={size} weight="duotone" />;
}

// hiển thị trạng thái

function StatusBadge({ status }: { status: string }) {
  const labelMap: Record<string, string> = {
    processing: 'Đang xử lý',
    ready: 'Sẵn sàng',
    error: 'Lỗi',
    pending: 'Đang chờ',
  };
  const label = labelMap[status] ?? status;
  return <span className={`cm-status-badge cm-status-${status}`}>{label}</span>;
}

// Component chính

export const CourseMaterials: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  const courseId = Number(id);
  const isValidCourseId = Number.isInteger(courseId) && courseId > 0;
  const initialCourse = isValidCourseId ? getCachedCourseById(courseId) : null;
  const initialMaterials = isValidCourseId ? getCachedMaterialsByCourse(courseId) : null;

  // Course info
  const [course, setCourse] = useState<Course | null>(initialCourse);
  const [courseLoading, setCourseLoading] = useState(!initialCourse);

  // Materials list
  const [materials, setMaterials] = useState<Material[]>(initialMaterials ?? []);
  const [listLoading, setListLoading] = useState(!initialMaterials);
  const [listError, setListError] = useState<string | null>(null);

  // Upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Toast
  const [toast, setToast] = useState<ToastState | null>(null);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch helpers

  const fetchCourse = useCallback(async () => {
    if (!id) return;
    const cachedCourse = getCachedCourseById(courseId);
    if (cachedCourse) setCourse(cachedCourse);
    setCourseLoading(!cachedCourse);
    try {
      const data = await fetchCourseById(courseId);
      setCourse(data);
    } catch (err: unknown) {
      console.error('[T020] fetchCourseById failed:', err);
    } finally {
      setCourseLoading(false);
    }
  }, [courseId, id]);

  const fetchMaterials = useCallback(async (silent = false) => {
    if (!id) return;
    const cachedMaterials = getCachedMaterialsByCourse(courseId);
    if (cachedMaterials) setMaterials(cachedMaterials);
    if (!silent) {
      setListLoading(!cachedMaterials);
      setListError(null);
    }
    try {
      const data = await getMaterialsByCourse(courseId);
      setMaterials(data);
    } catch (err: unknown) {
      console.error('[T020] getMaterialsByCourse failed:', err);
      if (!silent) setListError(extractApiError(err));
    } finally {
      if (!silent) setListLoading(false);
    }
  }, [courseId, id]);

  useEffect(() => {
    fetchCourse();
    fetchMaterials();

  }, [fetchCourse, fetchMaterials]);

  useEffect(() => {
    const hasProcessing = materials.some(m => m.status === 'processing' || m.status === 'pending');
    if (!hasProcessing) return;

    const interval = setInterval(() => {
      fetchMaterials(true);
    }, 5000);

    return () => clearInterval(interval);
  }, [materials, fetchMaterials]);

  // Toast helper
  const showToast = (type: 'success' | 'error', message: string) => {
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    setToast({ type, message });
    toastTimerRef.current = setTimeout(() => setToast(null), 4000);
  };

  // File selection & validation

  const handleFileSelect = (file: File) => {
    setUploadError(null);
    const err = validateFile(file);
    if (err) {
      setFileError(err);
      setSelectedFile(null);
    } else {
      setFileError(null);
      setSelectedFile(file);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
    e.target.value = '';
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setFileError(null);
    setUploadError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDownload = async (fileUrl: string, filename: string) => {
    try {
      await downloadMaterialFile(fileUrl, filename);
    } catch (error) {
      console.error('Download error:', error);
      showToast('error', 'Lỗi khi tải file. Vui lòng thử lại sau.');
    }
  };

  // Drag & Drop
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isUploading) setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (isUploading) return;
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(file);
  };

  // Upload
  const handleUpload = async () => {
    if (!selectedFile || !id) return;
    setIsUploading(true);
    setUploadError(null);
    try {
      await uploadMaterial(courseId, selectedFile);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      showToast('success', `Đã tải lên "${selectedFile.name}" thành công.`);
      await fetchMaterials();
    } catch (err: unknown) {
      console.error('[T020] uploadMaterial failed:', err);
      const msg = extractApiError(err);
      setUploadError(msg);
      showToast('error', msg);
    } finally {
      setIsUploading(false);
    }
  };

  // Render
  return (
    <div className="cm-container">

      {/* Toast notification */}
      {toast && (
        <div className={`cm-toast cm-toast-${toast.type}`} role="alert" aria-live="polite">
          {toast.type === 'success'
            ? <CheckCircle size={18} weight="fill" />
            : <WarningCircle size={18} weight="fill" />
          }
          <span>{toast.message}</span>
          <button
            className="cm-toast-close"
            onClick={() => setToast(null)}
            aria-label="Đóng thông báo"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Breadcrumb */}
      <nav className="cm-breadcrumb" aria-label="Breadcrumb">
        <ol className="cm-breadcrumb-list">
          <li className="cm-breadcrumb-item">
            <Link to="/courses" className="cm-breadcrumb-link">Môn học</Link>
          </li>
          <li className="cm-breadcrumb-separator" aria-hidden="true"><CaretRight size={14} weight="bold" /></li>
          <li className="cm-breadcrumb-item">
            <Link to={`/courses/${id}`} className="cm-breadcrumb-link cm-breadcrumb-course-name">
              {courseLoading ? 'Đang tải...' : (course?.title || 'Chi tiết môn học')}
            </Link>
          </li>
          <li className="cm-breadcrumb-separator" aria-hidden="true"><CaretRight size={14} weight="bold" /></li>
          <li className="cm-breadcrumb-item">
            <span className="cm-breadcrumb-current" aria-current="page">Tài liệu</span>
          </li>
        </ol>
      </nav>

      {/* Page header */}
      <div className="cm-page-header">
        <div className="cm-page-header-icon">
          <BookOpen size={22} weight="duotone" />
        </div>
        <div className="cm-page-header-info">
          {courseLoading ? (
            <div className="cm-header-skeleton" />
          ) : (
            <>
              <div className="cm-page-header-eyebrow">
                {course?.code && (
                  <span className="cm-course-code">{course.code}</span>
                )}
              </div>
              <h1 className="cm-page-title">
                {course?.title ?? 'Đang tải...'}
              </h1>
            </>
          )}
        </div>
      </div>

      {/* Upload card */}
      <div className="cm-card">
        <div className="cm-card-header">
          <h2 className="cm-card-title">Tải tài liệu</h2>
        </div>

        {/* Drop zone */}
        <div
          id="cm-upload-dropzone"
          className={`cm-dropzone ${isDragging ? 'cm-dropzone-dragging' : ''} ${isUploading ? 'cm-dropzone-disabled' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !isUploading && fileInputRef.current?.click()}
          role="button"
          tabIndex={isUploading ? -1 : 0}
          aria-label="Vùng kéo thả hoặc chọn file để tải lên"
          onKeyDown={(e) => {
            if ((e.key === 'Enter' || e.key === ' ') && !isUploading) {
              fileInputRef.current?.click();
            }
          }}
        >
          <input
            ref={fileInputRef}
            id="cm-file-input"
            type="file"
            accept={ALLOWED_EXTENSIONS.join(',')}
            onChange={handleInputChange}
            style={{ display: 'none' }}
            disabled={isUploading}
            aria-hidden="true"
          />

          {/* No file selected */}
          {!selectedFile && (
            <div className="cm-dropzone-empty">
              <div className="cm-dropzone-image">
                <img src="/upload_icon.png" alt="Tải lên tài liệu" />
              </div>
              <p className="cm-dropzone-primary">
                {isDragging ? 'Thả file vào đây' : 'Kéo thả hoặc click để chọn file'}
              </p>
              <p className="cm-dropzone-hint">
                {ALLOWED_EXTENSIONS.join(', ').toUpperCase()} · tối đa {MAX_FILE_SIZE_MB} MB
              </p>
            </div>
          )}

          {/* File selected */}
          {selectedFile && (
            <div
              className="cm-dropzone-selected"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="cm-file-icon-wrap">
                <FileIcon filename={selectedFile.name} size={22} />
              </div>
              <div className="cm-file-info">
                <span className="cm-file-name">{selectedFile.name}</span>
                <span className="cm-file-size">{formatFileSize(selectedFile.size)}</span>
              </div>
              <button
                className="cm-file-remove"
                onClick={handleClearFile}
                aria-label="Bỏ chọn file"
                disabled={isUploading}
              >
                <X size={16} />
              </button>
            </div>
          )}
        </div>

        {/* Validation error */}
        {fileError && (
          <div className="cm-inline-error" role="alert">
            <WarningCircle size={15} weight="fill" />
            {fileError}
          </div>
        )}

        {/* Upload error */}
        {uploadError && (
          <div className="cm-inline-error" role="alert">
            <WarningCircle size={15} weight="fill" />
            {uploadError}
          </div>
        )}

        {/* Submit button */}
        <div className="cm-upload-footer">
          <button
            id="cm-btn-upload"
            className="cm-btn-primary"
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            aria-disabled={!selectedFile || isUploading}
          >
            {isUploading ? (
              <>
                <CircleNotch size={16} weight="bold" className="cm-spin" />
                Đang tải lên...
              </>
            ) : (
              <>
                <UploadSimple size={16} weight="bold" />
                Tải lên tài liệu
              </>
            )}
          </button>
        </div>
      </div>

      {/* Materials list */}
      <div className="cm-card">
        <div className="cm-card-header cm-card-header-row">
          <div>
            <h2 className="cm-card-title">Danh sách tài liệu</h2>
            {!listLoading && !listError && (
              <p className="cm-card-subtitle">
                {materials.length === 0
                  ? 'Chưa có tài liệu nào'
                  : `${materials.length} tài liệu`}
              </p>
            )}
          </div>
        </div>

        {/* Loading */}
        {listLoading && (
          <div className="cm-list-loading">
            <CircleNotch size={22} weight="bold" className="cm-spin" />
            <span>Đang tải danh sách...</span>
          </div>
        )}

        {/* List error */}
        {!listLoading && listError && (
          <div className="cm-list-error" role="alert">
            <WarningCircle size={18} weight="fill" />
            <div>
              <p className="cm-list-error-msg">{listError}</p>
              <button className="cm-btn-retry" onClick={() => fetchMaterials()}>
                Thử lại
              </button>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!listLoading && !listError && materials.length === 0 && (
          <div className="cm-empty-state">
            <FolderDashed size={40} weight="duotone" />
            <p className="cm-empty-title">Chưa có tài liệu nào</p>
            <p className="cm-empty-desc">
              Tải lên file đầu tiên bằng khu vực phía trên.
            </p>
          </div>
        )}

        {/* Materials list */}
        {!listLoading && !listError && materials.length > 0 && (
          <ul className="cm-material-list" role="list">
            {materials.map((mat) => {
              const isProcessing = mat.status === 'processing' || mat.status === 'pending';
              return (
                <li key={mat.id} className="cm-material-item">
                  <div className="cm-material-icon">
                    <FileIcon filename={mat.title} size={18} />
                  </div>
                  <div className="cm-material-info">
                    <span className="cm-material-name" title={mat.title}>{mat.title}</span>
                    <span className="cm-material-date">
                      {formatViDate(mat.created_at)}
                    </span>
                  </div>
                  <StatusBadge status={mat.status} />
                  {isProcessing ? (
                    <span
                      className="cm-btn-download cm-btn-download-processing"
                      aria-label="File đang được xử lý, chưa thể tải xuống"
                      title="File đang được xử lý"
                    >
                      <CircleNotch size={15} weight="bold" className="cm-spin" />
                      <span>Đang xử lý</span>
                    </span>
                  ) : (
                    <button
                      type="button"
                      className="cm-btn-download"
                      aria-label={`Tải xuống ${mat.title}`}
                      title="Tải xuống"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDownload(mat.file_url, mat.title);
                      }}
                    >
                      <DownloadSimple size={16} weight="bold" />
                      <span>Tải xuống</span>
                    </button>
                  )}
                  <Link
                    to={`/courses/${courseId}/materials/${mat.id}`}
                    className="cm-icon-btn-detail"
                    title={`Xem chi tiết ${mat.title}`}
                    aria-label={`Xem chi tiết ${mat.title}`}
                  >
                    <CaretRight size={20} weight="bold" />
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </div>

      <div className="cm-footer-actions" style={{ display: 'flex', justifyContent: 'flex-start' }}>
        <Link
          to={`/courses/${courseId}`}
          className="cm-btn-back-outline"
        >
          <ArrowLeft size={16} /> Quay lại chi tiết môn học
        </Link>
      </div>
    </div>
  );
};
