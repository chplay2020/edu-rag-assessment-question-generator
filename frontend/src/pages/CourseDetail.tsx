import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  GraduationCap,
  Clock,
  User,
  Calendar,
  PencilSimple,
  ArrowSquareOut,
  BookOpen,
  Question
} from '@phosphor-icons/react';
import axios from 'axios';
import './CourseDetail.css';

interface Course {
  id: number;
  title: string;
  code: string;
  description: string;
  materialsCount?: number;
  questionsCount?: number;
  updated_at?: string | null;
  instructor?: string;
  semester?: string;
}

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

  const formatDate = (dateStr: string | null | undefined) => {
    if (!dateStr) return 'Vừa cập nhật';
    return new Date(dateStr).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  useEffect(() => {
    const loadCourse = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`http://localhost:8000/api/v1/courses/${id}`, { timeout: 3000 });
        if (response.data && response.data.id) {
          const mock = MOCK_COURSES.find(c => c.id === Number(id));
          setCourse({
            instructor: mock?.instructor ?? 'Giảng viên phụ trách',
            semester: mock?.semester ?? 'Học kỳ hiện tại',
            ...response.data,
            materialsCount: response.data.materialsCount ?? (mock?.materialsCount ?? Math.floor(Math.random() * 12) + 4),
            questionsCount: response.data.questionsCount ?? (mock?.questionsCount ?? Math.floor(Math.random() * 150) + 30),
          });
        } else {
          throw new Error('Not found');
        }
      } catch {
        const mock = MOCK_COURSES.find(c => c.id === Number(id));
        if (mock) {
          setCourse(mock);
        } else {
          setNotFound(true);
        }
      } finally {
        setIsLoading(false);
      }
    };
    loadCourse();
  }, [id]);

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

        {/* Header actions */}
        <div className="course-detail-header-actions">
          <button className="btn-action-disabled" disabled title="Chức năng thuộc task T016">
            <PencilSimple size={15} weight="bold" />
            Sửa môn học
          </button>
        </div>
      </div>

      {/* Info + Stats row */}
      <div className="course-detail-main-row">
        {/* Basic info card */}
        <div className="course-detail-info-card">
          <h2 className="course-detail-card-title">Thông tin cơ bản</h2>
          <div className="course-detail-info-list">
            <div className="info-row">
              <span className="info-icon"><User size={15} weight="duotone" /></span>
              <span className="info-label">Giảng viên</span>
              <span className="info-value">{course.instructor ?? '—'}</span>
            </div>
            <div className="info-row">
              <span className="info-icon"><Calendar size={15} weight="duotone" /></span>
              <span className="info-label">Học kỳ</span>
              <span className="info-value">{course.semester ?? '—'}</span>
            </div>
            <div className="info-row">
              <span className="info-icon"><Clock size={15} weight="duotone" /></span>
              <span className="info-label">Cập nhật</span>
              <span className="info-value">{formatDate(course.updated_at)}</span>
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
        <div className="course-detail-section-card">
          <div className="section-card-header">
            <div className="section-card-icon materials-icon">
              <BookOpen size={20} weight="duotone" />
            </div>
            <div>
              <h3 className="section-card-title">Tài liệu học tập</h3>
              <p className="section-card-count">{course.materialsCount} tài liệu</p>
            </div>
            <button className="btn-section-action" disabled title="Sẽ hoàn thiện trong task Material UI">
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
        <div className="course-detail-section-card">
          <div className="section-card-header">
            <div className="section-card-icon questions-icon">
              <Question size={20} weight="duotone" />
            </div>
            <div>
              <h3 className="section-card-title">Câu hỏi luyện tập</h3>
              <p className="section-card-count">{course.questionsCount} câu hỏi</p>
            </div>
            <button className="btn-section-action" disabled title="Sẽ hoàn thiện trong task Question Bank">
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
    </div>
  );
};
