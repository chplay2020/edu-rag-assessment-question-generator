import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import {
  GraduationCap,
  MagnifyingGlass,
  Plus,
  SquaresFour,
  Rows,
  BookOpen,
  Question,
  ArrowRight,
  FolderOpen,
  PencilSimple,
  X,
  DotsThreeVertical,
  Trash,
  WarningCircle
} from '@phosphor-icons/react';
import { CourseFormModal, type CourseFormPayload } from '../components/courses/CourseFormModal';
import { fetchCourses, createCourse, updateCourse, deleteCourse, type Course } from '../services/courseApi';
import './Courses.css';

export const Courses: React.FC = () => {
  const navigate = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isLoading, setIsLoading] = useState(true);

  // Độ trễ thanh tìm kiếm
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchQuery(searchQuery);
    }, 300);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // States for Dropdown & Delete Modal
  const [activeDropdownId, setActiveDropdownId] = useState<number | null>(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [courseToDelete, setCourseToDelete] = useState<Course | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  useEffect(() => {
    const handleClickOutside = () => setActiveDropdownId(null);
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // Load dữ liệu từ Course API (T014)
  const loadCourses = async () => {
    setIsLoading(true);
    try {
      const apiCourses = await fetchCourses();
      setCourses(apiCourses);
    } catch (err: any) {
      console.error('[T015] fetchCourses failed:', err);
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token');
        navigate('/login');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCourses();
  }, [navigate]);

  const handleOpenAddModal = () => {
    setSelectedCourse(null);
    setSubmitError(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (course: Course) => {
    setSelectedCourse(course);
    setSubmitError(null);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    if (isSubmitting) return;
    setIsModalOpen(false);
    setSubmitError(null);
  };

  const handleFormSubmit = async (payload: CourseFormPayload): Promise<void> => {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      if (selectedCourse) {
        // Sửa môn học
        const apiResult = await updateCourse(selectedCourse.id, {
          title: payload.title,
          code: payload.code || null,
          description: payload.description || null,
        });
        setCourses((prev) => prev.map((c) => (c.id === selectedCourse.id ? apiResult : c)));
      } else {
        // Tạo môn học mới
        const apiResult = await createCourse({
          title: payload.title,
          code: payload.code || null,
          description: payload.description || null,
        });
        setCourses((prev) => [apiResult, ...prev]);
      }
      setIsModalOpen(false);
      setSubmitError(null);
    } catch (err: unknown) {
      console.error('[T016] Course submit failed:', err);
      const axiosMsg =
        (err as { response?: { data?: { message?: string; detail?: string } } })
          ?.response?.data?.message ??
        (err as { response?: { data?: { message?: string; detail?: string } } })
          ?.response?.data?.detail ??
        null;
      setSubmitError(
        axiosMsg ??
        (selectedCourse
          ? 'Không thể cập nhật môn học. Vui lòng thử lại.'
          : 'Không thể tạo môn học. Vui lòng thử lại.')
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteCourse = async () => {
    if (!courseToDelete) return;
    setIsDeleting(true);
    setDeleteError(null);
    try {
      await deleteCourse(courseToDelete.id);
      setCourses((prev) => prev.filter((c) => c.id !== courseToDelete.id));
      setIsDeleteModalOpen(false);
      setCourseToDelete(null);
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

  const openDeleteModal = (course: Course) => {
    setCourseToDelete(course);
    setDeleteError(null);
    setIsDeleteModalOpen(true);
  };

  // Lọc danh sách môn học theo ô tìm kiếm
  const filteredCourses = courses.filter(course => {
    const query = debouncedSearchQuery.toLowerCase().trim();
    if (!query) return true;
    return (
      course.title.toLowerCase().includes(query) ||
      course.code.toLowerCase().includes(query) ||
      course.description.toLowerCase().includes(query)
    );
  });

  // Định dạng ngày hiển thị đẹp
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'Vừa cập nhật';
    const date = new Date(dateStr);
    return date.toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  // Variants định nghĩa as const để sửa lỗi biên dịch TS
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.04
      }
    }
  } as const;

  const itemVariants = {
    hidden: { opacity: 0, y: 12 },
    show: {
      opacity: 1,
      y: 0,
      transition: {
        type: 'spring' as const,
        stiffness: 260,
        damping: 22
      }
    }
  } as const;

  return (
    <motion.div
      className="courses-container"
      variants={containerVariants}
      initial="hidden"
      animate="show"
    >
      {/* Title Header */}
      <motion.div className="courses-header" variants={itemVariants}>
        <div className="courses-title-wrapper">
          <h2 className="courses-title">
            Môn học
          </h2>
          <p className="courses-subtitle">
            Quản lý danh sách môn học và tài liệu học tập của bạn.
          </p>
        </div>

        {/* Nút Thêm Môn Học */}
        <button
          onClick={handleOpenAddModal}
          className="btn-add-course"
          title="Thêm môn học mới"
        >
          <Plus size={16} weight="bold" />
          <span>Thêm môn học</span>
        </button>
      </motion.div>

      {/* Search & Tool Bar */}
      <motion.div className="courses-controls" variants={itemVariants}>
        {/* Search Input Container */}
        <div className="search-wrapper">
          <input
            type="text"
            placeholder="Tìm kiếm nhanh theo mã hoặc tên môn học..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">
            <MagnifyingGlass size={20} />
          </span>
          {searchQuery && (
            <button
              className="search-clear-btn"
              onClick={() => setSearchQuery('')}
              title="Xóa tìm kiếm"
            >
              <X size={14} weight="bold" />
            </button>
          )}
        </div>

        {/* Layout Toggle */}
        <div className="toggle-wrapper">
          <button
            onClick={() => setViewMode('grid')}
            className={`btn-toggle ${viewMode === 'grid' ? 'active' : ''}`}
            title="Dạng lưới"
          >
            <SquaresFour size={18} weight={viewMode === 'grid' ? 'fill' : 'regular'} />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`btn-toggle ${viewMode === 'list' ? 'active' : ''}`}
            title="Dạng danh sách"
          >
            <Rows size={18} weight={viewMode === 'list' ? 'fill' : 'regular'} />
          </button>
        </div>
      </motion.div>

      {/* Main List */}
      <div style={{ minHeight: '350px' }}>
        {isLoading ? (
          /* Loading indicator */
          <div className="loading-wrapper">
            <div className="loading-spinner"></div>
            <p className="loading-text">Đang kết nối cơ sở dữ liệu...</p>
          </div>
        ) : filteredCourses.length > 0 ? (
          <AnimatePresence mode="wait">
            {viewMode === 'grid' ? (
              /* Grid Layout Card List */
              <motion.div
                key="grid"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="courses-grid"
              >
                {filteredCourses.map((course) => (
                  <div key={course.id} className="course-card">
                    {/* Top Accent Gradient Header */}
                    <div className="course-card-accent" />

                    {/* Card Content */}
                    <div className="course-card-content">
                      {/* Header row */}
                      <div className="course-card-header">
                        <span className="course-code-badge">
                          {course.code}
                        </span>
                        {/* Stats Info on Top-Right */}
                        <div className="course-stats">
                          <div className="stat-item stat-item-materials">
                            <BookOpen size={14} weight="duotone" />
                            <span>{course.materialsCount} <span style={{ color: '#94a3b8', fontWeight: 'normal' }}>học liệu</span></span>
                          </div>
                          <div className="stat-item stat-item-questions">
                            <Question size={14} weight="duotone" />
                            <span>{course.questionsCount} <span style={{ color: '#94a3b8', fontWeight: 'normal' }}>câu hỏi</span></span>
                          </div>
                        </div>
                      </div>

                      {/* Title & Description */}
                      <h3 className="course-card-title">
                        {course.title}
                      </h3>
                      <p className="course-card-desc">
                        {course.description}
                      </p>

                      {/* Footer Area with Light Background */}
                      <div className="course-card-footer">
                        {/* Date info on Left */}
                        {course.updated_at ? (
                          <span className="course-card-time">
                            <span>Cập nhật: {formatDate(course.updated_at)}</span>
                          </span>
                        ) : (
                          <span className="course-card-time-empty" />
                        )}

                        <div className="course-card-actions-group">
                          <div className="course-card-dropdown-wrapper">
                            <button
                              className="btn-course-kebab"
                              onClick={(e) => {
                                e.stopPropagation();
                                setActiveDropdownId(activeDropdownId === course.id ? null : course.id);
                              }}
                              title="Tùy chọn"
                            >
                              <DotsThreeVertical size={20} weight="bold" />
                            </button>
                            
                            {activeDropdownId === course.id && (
                              <div className="course-card-dropdown-menu">
                                <button
                                  className="dropdown-item"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setActiveDropdownId(null);
                                    handleOpenEditModal(course);
                                  }}
                                >
                                  <PencilSimple size={16} />
                                  Sửa môn học
                                </button>
                                <button
                                  className="dropdown-item text-danger"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setActiveDropdownId(null);
                                    openDeleteModal(course);
                                  }}
                                >
                                  <Trash size={16} />
                                  Xóa môn học
                                </button>
                              </div>
                            )}
                          </div>

                          <button
                            onClick={() => navigate(`/courses/${course.id}`)}
                            className="btn-course-detail"
                          >
                            Xem chi tiết <ArrowRight size={14} weight="bold" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </motion.div>
            ) : (
              /* Card-Based Table List View */
              <motion.div
                key="list"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="courses-table-container"
              >
                {/* Custom Table Header */}
                <div className="courses-table-header">
                  <div>Mã môn</div>
                  <div>Tên môn học</div>
                  <div className="table-desc-header">Mô tả chi tiết</div>
                  <div style={{ textAlign: 'center' }}>Học liệu</div>
                  <div style={{ textAlign: 'center' }}>Bộ câu hỏi</div>
                  <div style={{ textAlign: 'center' }}>Cập nhật cuối</div>
                  <div></div>
                </div>

                {/* Custom Card Rows */}
                {filteredCourses.map((course) => (
                  <div
                    key={course.id}
                    className="table-row-card"
                    onClick={() => navigate(`/courses/${course.id}`)}
                  >
                    <div className="table-code-cell">
                      <span className="table-code-badge">
                        {course.code}
                      </span>
                    </div>
                    <div>
                      <div className="table-title">
                        {course.title}
                      </div>
                    </div>
                    <div className="table-desc-cell">
                      <div className="table-desc">
                        {course.description}
                      </div>
                    </div>
                    <div className="table-stat-cell">
                      <div className="table-stat table-stat-materials">
                        <BookOpen size={14} />
                        <span>{course.materialsCount}</span>
                      </div>
                    </div>
                    <div className="table-stat-cell">
                      <div className="table-stat table-stat-questions">
                        <Question size={14} />
                        <span>{course.questionsCount}</span>
                      </div>
                    </div>
                    <div className="table-time-cell">
                      <div className="table-time">
                        {course.updated_at ? formatDate(course.updated_at) : '—'}
                      </div>
                    </div>
                    <div className="table-arrow-cell">
                      <div className="course-card-dropdown-wrapper" style={{ position: 'relative' }}>
                        <button
                          className="btn-course-kebab"
                          onClick={(e) => {
                            e.stopPropagation();
                            setActiveDropdownId(activeDropdownId === course.id ? null : course.id);
                          }}
                          title="Tùy chọn"
                        >
                          <DotsThreeVertical size={20} weight="bold" />
                        </button>
                        
                        {activeDropdownId === course.id && (
                          <div className="course-card-dropdown-menu" style={{ right: 0, top: '100%', zIndex: 10 }}>
                            <button
                              className="dropdown-item"
                              onClick={(e) => {
                                e.stopPropagation();
                                setActiveDropdownId(null);
                                handleOpenEditModal(course);
                              }}
                            >
                              <PencilSimple size={16} />
                              Sửa môn học
                            </button>
                            <button
                              className="dropdown-item text-danger"
                              onClick={(e) => {
                                e.stopPropagation();
                                setActiveDropdownId(null);
                                openDeleteModal(course);
                              }}
                            >
                              <Trash size={16} />
                              Xóa môn học
                            </button>
                          </div>
                        )}
                      </div>

                      <button
                        className="btn-table-detail"
                        onClick={(e) => { e.stopPropagation(); navigate(`/courses/${course.id}`); }}
                      >
                        <span>Xem chi tiết</span> <ArrowRight size={13} weight="bold" />
                      </button>
                    </div>
                  </div>
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        ) : courses.length === 0 && !searchQuery.trim() ? (
          // Ko có môn học
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="empty-state-compact"
          >
            <div className="empty-state-compact-icon">
              <FolderOpen size={36} weight="duotone" />
            </div>
            <h4 className="empty-state-compact-title">
              Bạn chưa có môn học nào
            </h4>
            <p className="empty-state-compact-desc">
              Tạo không gian đầu tiên để lưu trữ tài liệu và ngân hàng câu hỏi.
            </p>
            <button
              onClick={handleOpenAddModal}
              className="btn-add-course"
              style={{ marginTop: '16px' }}
            >
              <Plus size={16} weight="bold" style={{ marginRight: '6px' }} />
              Thêm môn học
            </button>
          </motion.div>
        ) : (
          // Ko có môn học khi search
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="empty-state-compact"
          >
            <div className="empty-state-compact-icon">
              <FolderOpen size={36} weight="duotone" />
            </div>
            <h4 className="empty-state-compact-title">
              Không tìm thấy môn học nào
            </h4>
            <p className="empty-state-compact-desc">
              Không tìm thấy môn học nào phù hợp với từ khóa "{searchQuery}". Hãy thử điều chỉnh hoặc xóa từ khóa tìm kiếm.
            </p>
            <button
              onClick={() => setSearchQuery('')}
              className="btn-clear-search"
            >
              Xóa bộ lọc tìm kiếm
            </button>
          </motion.div>
        )}
      </div>

      <CourseFormModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        onSubmit={handleFormSubmit}
        course={selectedCourse}
        existingCourses={courses}
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
                Môn học <strong>{courseToDelete?.code} - {courseToDelete?.title}</strong> và toàn bộ tài liệu liên quan sẽ bị xóa khỏi hệ thống. Hành động này không thể phục hồi.
              </p>
              
              {deleteError && (
                <div style={{ marginBottom: '20px', padding: '12px 16px', backgroundColor: '#fef2f2', borderLeft: '4px solid #dc2626', color: '#991b1b', fontSize: '0.9rem', borderRadius: '4px' }}>
                  {deleteError}
                </div>
              )}

              <div className="modal-footer" style={{ display: 'flex', gap: '12px', padding: 0, borderTop: 'none', backgroundColor: 'transparent', justifyContent: 'flex-end' }}>
                <button 
                  type="button" 
                  className="btn-secondary" 
                  style={{ padding: '10px 20px', borderRadius: '10px', border: '1px solid #cbd5e1', backgroundColor: '#fff', cursor: 'pointer', fontWeight: 600, color: '#475569' }}
                  onClick={() => setIsDeleteModalOpen(false)} 
                  disabled={isDeleting}
                >
                  Hủy
                </button>
                <button 
                  type="button" 
                  className="btn-primary" 
                  style={{ padding: '10px 20px', borderRadius: '10px', backgroundColor: '#dc2626', color: '#fff', border: 'none', cursor: 'pointer', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}
                  onClick={handleDeleteCourse} 
                  disabled={isDeleting}
                >
                  <Trash size={16} weight="bold" />
                  {isDeleting ? 'Đang xóa...' : 'Xóa vĩnh viễn'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};
