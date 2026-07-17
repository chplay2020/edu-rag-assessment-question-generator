import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  GraduationCap,
  User,
  Calendar,
  PencilSimple,
  ArrowSquareOut,
  BookOpen,
  Question
} from '@phosphor-icons/react';
import { CourseFormModal } from '../components/courses/CourseFormModal';
import { fetchCourseById, type Course } from '../services/courseApi';
import './CourseDetail.css';

// Mock Fallback Data
// Dùng khi backend chưa chạy hoặc API lỗi.
const MOCK_COURSES: Course[] = [
  { id: 1, title: 'Lập trình Web nâng cao', code: 'INT3306', description: 'Xây dựng ứng dụng web hiện đại sử dụng React, Node.js, và các công nghệ Cloud tiên tiến.', materialsCount: 12, questionsCount: 160, updated_at: '2026-07-14T08:30:00Z', instructor: 'TS. Nguyễn Văn An', semester: 'Học kỳ 2 – 2025-2026' },
  { id: 2, title: 'Cơ sở dữ liệu', code: 'INT2208', description: 'Nguyên lý thiết kế cơ sở dữ liệu quan hệ, ngôn ngữ truy vấn SQL và tối ưu hóa hệ quản trị CSDL.', materialsCount: 8, questionsCount: 120, updated_at: '2026-07-13T10:15:00Z', instructor: 'PGS. Trần Thị Bình', semester: 'Học kỳ 2 – 2025-2026' },
  { id: 3, title: 'Trí tuệ nhân tạo', code: 'INT3401', description: 'Tìm hiểu các thuật toán tìm kiếm, biểu diễn tri thức, học máy (Machine Learning) và mạng nơ-ron.', materialsCount: 15, questionsCount: 240, updated_at: '2026-07-12T14:45:00Z', instructor: 'GS. Lê Hoàng Cường', semester: 'Học kỳ 1 – 2025-2026' },
  { id: 4, title: 'Mạng máy tính', code: 'INT2215', description: 'Kiến trúc phân tầng của mạng máy tính, các giao thức mạng phổ biến TCP/IP và bảo mật mạng cơ bản.', materialsCount: 10, questionsCount: 150, updated_at: '2026-07-08T16:20:00Z', instructor: 'TS. Phạm Minh Đức', semester: 'Học kỳ 1 – 2025-2026' },
];


export const CourseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<Course | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  // States cho modal sửa
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [allCourses, setAllCourses] = useState<Course[]>([]);

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return 'Vừa cập nhật';
    return new Date(dateStr).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  // Load chi tiết môn học từ API, fallback về mock nếu lỗi 
  useEffect(() => {
    if (!id) {
      setNotFound(true);
      setIsLoading(false);
      return;
    }

    let cancelled = false;
    const numericId = Number(id);

    const loadCourse = async () => {
      setIsLoading(true);
      try {
        const apiCourse = await fetchCourseById(numericId);
        if (cancelled) return;

        if (apiCourse === null) {
          // Backend trả 404 → không tìm thấy thật sự
          setNotFound(true);
        } else {
          setCourse(apiCourse);
          setAllCourses([apiCourse]);
        }
      } catch (err) {
        // Lỗi kết nối hoặc backend chưa chạy → fallback về mock
        console.warn('[T015] fetchCourseById failed, falling back to mock:', err);
        if (!cancelled) {
          const mock = MOCK_COURSES.find((c) => c.id === numericId);
          if (mock) {
            setCourse(mock);
            setAllCourses(MOCK_COURSES);
          } else {
            setNotFound(true);
          }
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    };

    loadCourse();
    return () => { cancelled = true; };
  }, [id]);

  const handleOpenEditModal = () => {
    setIsModalOpen(true);
  };


  const handleFormSubmit = (courseData: Omit<Course, 'materialsCount' | 'questionsCount'>) => {
    if (!course) return;
    const updatedCourse: Course = {
      ...course,
      ...courseData,
      updated_at: new Date().toISOString(),
    };
    setCourse(updatedCourse);
    const updatedList = allCourses.map((c) => (c.id === course.id ? updatedCourse : c));
    setAllCourses(updatedList);
    setIsModalOpen(false);
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

  if (notFound || !course) {
    return (
      <div className="course-detail-container">
        <button className="btn-back" onClick={() => navigate('/courses')}>
          <ArrowLeft size={16} weight="bold" /> Quay lại danh sách
        </button>
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
      {/* Back button */}
      <button className="btn-back" onClick={() => navigate('/courses')}>
        <ArrowLeft size={16} weight="bold" /> Quay lại danh sách môn học
      </button>

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

      {/* Info + Stats row */}
      <div className="course-detail-main-row">
        {/* Basic info card */}
        <div className="course-detail-info-card">
          <div className="course-detail-card-header-row">
            <h2 className="course-detail-card-title" style={{ marginBottom: 0 }}>Thông tin cơ bản</h2>
            <div className="course-detail-updated-inline">
              <span>Cập nhật: {formatDate(course.updated_at)}</span>
            </div>
          </div>
          <div className="course-detail-info-list info-chip-list">
            <div className="info-chip-row">
              <div className="info-chip-icon-wrapper">
                <User size={16} weight="duotone" />
              </div>
              <div className="info-chip-content">
                <span className="info-chip-label">Giảng viên</span>
                <span className="info-chip-value">{course.instructor ?? '—'}</span>
              </div>
            </div>
            <div className="info-chip-row">
              <div className="info-chip-icon-wrapper">
                <Calendar size={16} weight="duotone" />
              </div>
              <div className="info-chip-content">
                <span className="info-chip-label">Học kỳ</span>
                <span className="info-chip-value">{course.semester ?? '—'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Description card */}
        <div className="course-detail-info-card">
          <h2 className="course-detail-card-title">Mô tả môn học</h2>
          <p className="course-detail-desc" style={{ marginTop: '0' }}>{course.description}</p>
        </div>
      </div>

      {/* Placeholder sections */}
      <div className="course-detail-sections-row">
        {/* Materials placeholder */}
        <div className="course-detail-section-card panel-materials">
          <div className="section-card-header">
            <div className="section-card-icon materials-icon">
              <BookOpen size={20} weight="duotone" />
            </div>
            <div>
              <h3 className="section-card-title">Tài liệu học tập</h3>
              <p className="section-card-count">{course.materialsCount} tài liệu</p>
            </div>
            <button className="btn-section-action disabled-materials" disabled title="Sẽ hoàn thiện trong task Material UI">
              <ArrowSquareOut size={14} weight="bold" />
              Xem tài liệu
            </button>
          </div>
          <div className="section-card-placeholder">
            <p>Danh sách tài liệu học tập sẽ được hiển thị sau khi hoàn thành <strong>Material UI</strong>.</p>
            <p className="section-notice">Thông tin chi tiết sẽ được hoàn thiện trong các task quản lý học liệu và ngân hàng câu hỏi tiếp theo.</p>
          </div>
        </div>

        {/* Questions placeholder */}
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
            <p className="section-notice">Thông tin chi tiết sẽ được hoàn thiện trong các task quản lý học liệu và ngân hàng câu hỏi tiếp theo.</p>
          </div>
        </div>
      </div>

      <CourseFormModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleFormSubmit}
        course={course}
        existingCourses={allCourses}
      />
    </div>
  );
};
