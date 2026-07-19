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
  PencilSimple
} from '@phosphor-icons/react';
import { CourseFormModal, type CourseFormPayload } from '../components/courses/CourseFormModal';
import { fetchCourses, createCourse, updateCourse, saveLocalUiExtras, type Course } from '../services/courseApi';
import './Courses.css';

// Mock Fallback Data
// Dùng khi backend chưa chạy hoặc API lỗi.
const MOCK_COURSES: Course[] = [
  {
    id: 1,
    title: 'Lập trình Web nâng cao',
    code: 'INT3306',
    description: 'Xây dựng ứng dụng web hiện đại sử dụng React, Node.js, và các công nghệ Cloud tiên tiến.',
    materialsCount: 12,
    questionsCount: 160,
    updated_at: '2026-07-14T08:30:00Z',
    instructor: 'TS. Nguyễn Văn An',
  },
  {
    id: 2,
    title: 'Cơ sở dữ liệu',
    code: 'INT2208',
    description: 'Nguyên lý thiết kế cơ sở dữ liệu quan hệ, ngôn ngữ truy vấn SQL và tối ưu hóa hệ quản trị CSDL.',
    materialsCount: 8,
    questionsCount: 120,
    updated_at: '2026-07-13T10:15:00Z',
    instructor: 'PGS. Trần Thị Bình',
  },
  {
    id: 3,
    title: 'Trí tuệ nhân tạo',
    code: 'INT3401',
    description: 'Tìm hiểu các thuật toán tìm kiếm, biểu diễn tri thức, học máy (Machine Learning) và mạng nơ-ron.',
    materialsCount: 15,
    questionsCount: 240,
    updated_at: '2026-07-12T14:45:00Z',
    instructor: 'GS. Lê Hoàng Cường',
  },
  {
    id: 4,
    title: 'Mạng máy tính',
    code: 'INT2215',
    description: 'Kiến trúc phân tầng của mạng máy tính, các giao thức mạng phổ biến TCP/IP và bảo mật mạng cơ bản.',
    materialsCount: 10,
    questionsCount: 150,
    updated_at: '2026-07-08T16:20:00Z',
    instructor: 'TS. Phạm Minh Đức',
  },
];

export const Courses: React.FC = () => {
  const navigate = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isLoading, setIsLoading] = useState(true);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Load dữ liệu từ Course API (T014), fallback về mock nếu lỗi 
  useEffect(() => {
    let cancelled = false;
    const loadCourses = async () => {
      setIsLoading(true);
      try {
        const apiCourses = await fetchCourses();
        if (!cancelled) {
          setCourses(apiCourses);
        }
      } catch (err) {
        // API lỗi hoặc backend chưa chạy → dùng mock data
        console.warn('[T015] fetchCourses failed, using mock data:', err);
        if (!cancelled) {
          setCourses(MOCK_COURSES);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };
    loadCourses();
    return () => { cancelled = true; };
  }, []);

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
        saveLocalUiExtras(selectedCourse.id, payload.instructor);
        const merged = {
          ...apiResult,
          instructor: payload.instructor || selectedCourse.instructor,
        };
        setCourses((prev) => prev.map((c) => (c.id === selectedCourse.id ? merged : c)));
      } else {
        // Tạo môn học mới
        const apiResult = await createCourse({
          title: payload.title,
          code: payload.code || null,
          description: payload.description || null,
        });

        saveLocalUiExtras(apiResult.id, payload.instructor);

        const merged = {
          ...apiResult,
          instructor: payload.instructor || apiResult.instructor,
        };
        setCourses((prev) => [merged, ...prev]);
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

  // Lọc danh sách môn học theo ô tìm kiếm
  const filteredCourses = courses.filter(course => {
    const query = searchQuery.toLowerCase().trim();
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
            <span className="courses-title-icon">
              <GraduationCap size={24} weight="duotone" />
            </span>
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
            placeholder="Tìm kiếm nhanh theo mã, tên hoặc mô tả môn học..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <span className="search-icon">
            <MagnifyingGlass size={20} />
          </span>
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
                          <button
                            className="btn-card-edit"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleOpenEditModal(course);
                            }}
                            title="Sửa môn học"
                            aria-label="Sửa môn học"
                          >
                            <PencilSimple size={14} />
                            <span>Sửa</span>
                          </button>
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
                      <button
                        className="btn-table-edit"
                        onClick={(e) => { e.stopPropagation(); handleOpenEditModal(course); }}
                        title="Sửa môn học"
                      >
                        <PencilSimple size={13} />
                        <span>Sửa</span>
                      </button>
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
        ) : (
          /* Empty Search Results */
          <motion.div
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="empty-state"
          >
            <div className="empty-state-icon">
              <FolderOpen size={30} weight="duotone" />
            </div>
            <h4 className="empty-state-title">
              Không tìm thấy môn học nào
            </h4>
            <p className="empty-state-desc">
              Không tìm thấy môn học nào phù hợp với từ khóa "{searchQuery}". Hãy thử thay đổi bộ lọc hoặc xóa từ khóa tìm kiếm.
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
    </motion.div>
  );
};
