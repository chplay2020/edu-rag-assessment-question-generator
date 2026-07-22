import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  GraduationCap,
  User,
  PencilSimple,
  ArrowSquareOut,
  BookOpen,
  Question,
  Trash,
  X,
  CaretRight
} from '@phosphor-icons/react';
import { CourseFormModal, type CourseFormPayload } from '../components/courses/CourseFormModal';
import { fetchCourseById, updateCourse, deleteCourse, type Course } from '../services/courseApi';
import { getMaterialsByCourse } from '../services/materialApi';
import './CourseDetail.css';
export const CourseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<Course | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [pageError, setPageError] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // States for Delete Modal
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // real materials count
  const [materialsCount, setMaterialsCount] = useState<number | null>(null);

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return 'Vừa cập nhật';
    return new Date(dateStr).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  const fetchData = async () => {
    if (!id) {
      setNotFound(true);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setNotFound(false);
    setPageError(null);

    try {
      const apiCourse = await fetchCourseById(Number(id));
      if (apiCourse === null) {
        setNotFound(true);
      } else {
        setCourse(apiCourse);
      }
    } catch (err: any) {
      console.error('[T015] fetchCourseById failed:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token');
        navigate('/login');
      } else if (err.response?.status === 404) {
        setNotFound(true);
      } else {
        setPageError('Đã xảy ra lỗi khi tải thông tin môn học.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id, navigate]);

  // fetch real materials count when course id changes
  useEffect(() => {
    if (!id) return;
    getMaterialsByCourse(Number(id))
      .then((list) => setMaterialsCount(list.length))
      .catch(() => setMaterialsCount(null));
  }, [id]);

  const handleOpenEditModal = () => {
    setSubmitError(null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    if (isSubmitting) return;
    setIsModalOpen(false);
    setSubmitError(null);
  };


  const handleFormSubmit = async (payload: CourseFormPayload): Promise<void> => {
    if (!course) return;
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const apiResult = await updateCourse(course.id, {
        title: payload.title,
        code: payload.code || null,
        description: payload.description || null,
      });

      setCourse(apiResult);
      setIsModalOpen(false);
      setSubmitError(null);
    } catch (err: unknown) {
      console.error('[T016] updateCourse failed:', err);
      const axiosMsg =
        (err as { response?: { data?: { message?: string; detail?: string } } })
          ?.response?.data?.message ??
        (err as { response?: { data?: { message?: string; detail?: string } } })
          ?.response?.data?.detail ??
        null;
      setSubmitError(
        axiosMsg ?? 'Không thể cập nhật môn học. Vui lòng thử lại.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteCourse = async () => {
    if (!course) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await deleteCourse(course.id);
      setIsDeleteModalOpen(false);
      navigate('/courses');
    } catch (err: unknown) {
      console.error('[T017] deleteCourse failed:', err);
      const axiosMsg =
        (err as { response?: { data?: { message?: string; detail?: string } } })
          ?.response?.data?.message ??
        (err as { response?: { data?: { message?: string; detail?: string } } })
          ?.response?.data?.detail ??
        null;
      setDeleteError(
        axiosMsg ?? 'Không thể xóa môn học. Vui lòng thử lại sau.'
      );
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="course-detail-container">
        <div className="course-detail-loading">
          <div className="loading-spinner"></div>
          <p>Đang tải thông tin môn học...</p>
        </div>
      </div>
    );
  }

  if (pageError) {
    return (
      <div className="course-detail-container">
        <button className="btn-back" onClick={() => navigate('/courses')}>
          <ArrowLeft size={16} weight="bold" /> Quay lại danh sách
        </button>
        <div className="course-detail-not-found">
          <Question size={48} weight="duotone" color="#dc2626" />
          <h2>Đã xảy ra lỗi</h2>
          <p>{pageError}</p>
          <button
            className="btn-action-edit"
            style={{ marginTop: '16px', border: '1px solid #ccc' }}
            onClick={fetchData}
          >
            Thử lại
          </button>
        </div>
      </div>
    );
  }

  if (notFound || !course) {
    return (
      <div className="course-detail-container">
        <nav className="cm-breadcrumb" aria-label="Breadcrumb">
          <ol className="cm-breadcrumb-list">
            <li className="cm-breadcrumb-item">
              <Link to="/courses" className="cm-breadcrumb-link">Môn học</Link>
            </li>
            <li className="cm-breadcrumb-separator" aria-hidden="true"><CaretRight size={14} weight="bold" /></li>
            <li className="cm-breadcrumb-item">
              <span className="cm-breadcrumb-current" aria-current="page">Chi tiết môn học</span>
            </li>
          </ol>
        </nav>
        <div className="course-detail-not-found">
          <GraduationCap size={48} weight="duotone" />
          <h2>Không tìm thấy môn học</h2>
          <p>Môn học với mã <strong>#{id}</strong> không tồn tại hoặc đã bị xóa.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="course-detail-container">
      {/* Breadcrumb */}
      <nav className="cm-breadcrumb" aria-label="Breadcrumb">
        <ol className="cm-breadcrumb-list">
          <li className="cm-breadcrumb-item">
            <Link to="/courses" className="cm-breadcrumb-link">Môn học</Link>
          </li>
          <li className="cm-breadcrumb-separator" aria-hidden="true"><CaretRight size={14} weight="bold" /></li>
          <li className="cm-breadcrumb-item">
            <span className="cm-breadcrumb-current cm-breadcrumb-course-name" aria-current="page">
              {course.title}
            </span>
          </li>
        </ol>
      </nav>

      {/* Header Card */}
      <div className="course-detail-header-card">
        <div className="course-detail-header-left">
          <div className="course-detail-icon">
            <GraduationCap size={32} weight="duotone" />
          </div>
          <div className="course-detail-header-info">
            <div className="course-detail-header-meta">
              <span className="course-detail-code">{course.code}</span>
            </div>
            <h1 className="course-detail-title">{course.title}</h1>
          </div>
        </div>

        {/* Header Right (Actions) */}
        <div className="course-detail-header-right">
          <div className="course-detail-header-actions">
            <button className="btn-action-edit" onClick={handleOpenEditModal}>
              <PencilSimple size={15} weight="bold" />
              Sửa môn học
            </button>
          </div>
        </div>
      </div>

      {/* Body Layout (Main / Sidebar) */}
      <div className="course-detail-body-layout">

        <div className="course-detail-main-col">
          {/* Description card */}
          <div className="course-detail-info-card">
            <h2 className="course-detail-card-title">Mô tả môn học</h2>
            <p className="course-detail-desc" style={{ marginTop: '0' }}>{course.description}</p>
          </div>

          {/* Tài liệu học tập */}
          <div className="course-detail-section-card panel-materials">
            <div className="section-card-header">
              <div className="section-card-icon materials-icon">
                <BookOpen size={20} weight="duotone" />
              </div>
              <div>
                <h3 className="section-card-title">Tài liệu học tập</h3>
                <p className="section-card-count">
                  {materialsCount === null ? '—' : `${materialsCount} tài liệu`}
                </p>
              </div>
              <button
                className="btn-section-action btn-section-materials-active"
                onClick={() => navigate(`/courses/${id}/materials`)}
                title="Quản lý tài liệu học tập"
              >
                <ArrowSquareOut size={14} weight="bold" />
                Quản lý tài liệu
              </button>
            </div>
            <div className="section-card-placeholder">
              <p>Xem, tải lên và quản lý toàn bộ tài liệu học tập của môn học này.</p>
            </div>
          </div>

          {/* Câu hỏi luyện tập */}
          <div className="course-detail-section-card panel-questions">
            <div className="section-card-header">
              <div className="section-card-icon questions-icon">
                <Question size={20} weight="duotone" />
              </div>
              <div>
                <h3 className="section-card-title">Câu hỏi luyện tập</h3>
                <p className="section-card-count">{course.questionsCount} câu hỏi</p>
              </div>
              <button className="btn-section-action disabled-questions" disabled title="Sẽ hoàn thiện trong task Question Bank">
                <ArrowSquareOut size={14} weight="bold" />
                Xem câu hỏi
              </button>
            </div>
            <div className="section-card-placeholder">
              <p>Câu hỏi thuộc môn học sẽ được hiển thị sau khi hoàn thành <strong>Question Bank</strong>.</p>
            </div>
          </div>

          <div className="cd-footer-actions" style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <Link
              to={`/courses`}
              className="cd-btn-back-outline"
            >
              <ArrowLeft size={16} /> Quay lại danh sách môn học
            </Link>
          </div>
        </div>
        <div className="course-detail-sidebar-col">
          <div className="course-detail-info-card">
            <div className="course-detail-card-header-row">
              <h2 className="course-detail-card-title" style={{ marginBottom: 0 }}>Thông tin cơ bản</h2>
            </div>
            <div className="course-detail-updated-inline" style={{ marginBottom: '16px' }}>
              <span>Cập nhật: {formatDate(course.updated_at)}</span>
            </div>
            <div className="course-detail-info-list info-chip-list" style={{ flexDirection: 'column' }}>
              <div className="info-chip-row">
                <div className="info-chip-icon-wrapper">
                  <User size={16} weight="duotone" />
                </div>
                <div className="info-chip-content">
                  <span className="info-chip-label">Giảng viên</span>
                  <span className="info-chip-value">{course.instructor ?? '—'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* DANGER ZONE */}
          <div className="course-detail-danger-zone" style={{ marginTop: 0 }}>
            <div className="danger-zone-info">
              <h3>Xóa môn học này</h3>
              <p>Môn học sẽ bị ẩn khỏi danh sách và không thể sử dụng tiếp.</p>
            </div>
            <button className="btn-danger-outline" onClick={() => setIsDeleteModalOpen(true)}>
              <Trash size={16} />
              Xóa môn học
            </button>
          </div>
        </div>
      </div>

      <CourseFormModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleFormSubmit}
        course={course}
        existingCourses={course ? [course] : []}
        isSubmitting={isSubmitting}
        submitError={submitError}
      />

      {/* Delete Confirmation Modal */}
      {isDeleteModalOpen && (
        <div className="modal-backdrop" onClick={isDeleting ? undefined : () => setIsDeleteModalOpen(false)}>
          <div className="modal-container delete-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-header-title-area">
                <div style={{ display: 'flex', alignItems: 'center' }}>
                  <h3 style={{ margin: 0, color: '#0f172a', fontSize: '1.15rem', fontWeight: 700 }}>Xóa môn học</h3>
                </div>
              </div>
              <button
                className="btn-close"
                onClick={() => setIsDeleteModalOpen(false)}
                aria-label="Đóng"
                disabled={isDeleting}
              >
                <X size={20} />
              </button>
            </div>
            <div className="modal-form" style={{ padding: '12px 32px 24px 32px' }}>
              <p style={{ margin: '0 0 8px 0', fontSize: '0.95rem', color: '#475569', lineHeight: 1.5 }}>
                Môn học <strong>{course?.code} - {course?.title}</strong> và toàn bộ tài liệu, câu hỏi liên quan sẽ bị xóa khỏi hệ thống. Hành động này không thể phục hồi.
              </p>

              {deleteError && (
                <div style={{ marginBottom: '20px', padding: '12px 16px', backgroundColor: '#fef2f2', borderLeft: '4px solid #dc2626', color: '#991b1b', fontSize: '0.9rem', borderRadius: '4px' }}>
                  {deleteError}
                </div>
              )}

              <div className="modal-footer" style={{ display: 'flex', gap: '12px', padding: 0, borderTop: 'none', backgroundColor: 'transparent', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  className="btn-cancel"
                  onClick={() => setIsDeleteModalOpen(false)}
                  disabled={isDeleting}
                >
                  Hủy
                </button>
                <button
                  type="button"
                  className="btn-danger"
                  onClick={handleDeleteCourse}
                  disabled={isDeleting}
                >
                  <Trash size={16} weight="bold" />
                  {isDeleting ? 'Đang xóa...' : 'Xóa môn học'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
