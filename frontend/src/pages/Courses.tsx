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
  Clock,
  ArrowRight,
  FolderOpen
} from '@phosphor-icons/react';
import axios from 'axios';
import './Courses.css';

// Interface dữ liệu môn học
interface Course {
  id: number;
  title: string;
  code: string;
  description: string;
  materialsCount: number; // mock
  questionsCount: number; // mock
  updated_at: string | null;
}

// Mock Data 
const MOCK_COURSES: Course[] = [
  {
    id: 1,
    title: 'Lập trình Web nâng cao',
    code: 'INT3306',
    description: 'Xây dựng ứng dụng web hiện đại sử dụng React, Node.js, và các công nghệ Cloud tiên tiến.',
    materialsCount: 12,
    questionsCount: 160,
    updated_at: '2026-07-14T08:30:00Z',
  },
  {
    id: 2,
    title: 'Cơ sở dữ liệu',
    code: 'INT2208',
    description: 'Nguyên lý thiết kế cơ sở dữ liệu quan hệ, ngôn ngữ truy vấn SQL và tối ưu hóa hệ quản trị CSDL.',
    materialsCount: 8,
    questionsCount: 120,
    updated_at: '2026-07-13T10:15:00Z',
  },
  {
    id: 3,
    title: 'Trí tuệ nhân tạo',
    code: 'INT3401',
    description: 'Tìm hiểu các thuật toán tìm kiếm, biểu diễn tri thức, học máy (Machine Learning) và mạng nơ-ron.',
    materialsCount: 15,
    questionsCount: 240,
    updated_at: '2026-07-12T14:45:00Z',
  },
  {
    id: 4,
    title: 'Mạng máy tính',
    code: 'INT2215',
    description: 'Kiến trúc phân tầng của mạng máy tính, các giao thức mạng phổ biến TCP/IP và bảo mật mạng cơ bản.',
    materialsCount: 10,
    questionsCount: 150,
    updated_at: '2026-07-08T16:20:00Z',
  },
];

export const Courses: React.FC = () => {
  const navigate = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isLoading, setIsLoading] = useState(true);

  // Gọi API lấy dữ liệu môn học thực tế từ backend
  useEffect(() => {
    const loadCourses = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get('http://localhost:8000/api/v1/courses', {
          timeout: 3000
        });

        if (Array.isArray(response.data)) {
          const mappedCourses = response.data.map((c: any) => ({
            id: c.id,
            title: c.title,
            code: c.code || 'MÃ MÔN',
            description: c.description || 'Chưa có mô tả cho môn học này.',
            materialsCount: Math.floor(Math.random() * 12) + 4,
            questionsCount: Math.floor(Math.random() * 150) + 30,
            updated_at: c.updated_at || c.created_at || null,
          }));
          setCourses(mappedCourses);
        } else {
          throw new Error('Dữ liệu sai định dạng');
        }
      } catch (err) {
        console.warn('Backend API connection failed, switching to Mock Data', err);
        setCourses(MOCK_COURSES);
      } finally {
        setIsLoading(false);
      }
    };

    loadCourses();
  }, []);

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

        {/* Nút Thêm Môn Học (Disabled) */}
        <button
          disabled
          className="btn-add-course"
          title="Tính năng thêm môn học sẽ có ở T016"
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
                        {course.updated_at && (
                          <span className="course-card-time">
                            <Clock size={14} />
                            {formatDate(course.updated_at)}
                          </span>
                        )}
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
                        {/* Stats Info */}
                        <div className="course-stats">
                          <div className="stat-item stat-item-materials">
                            <BookOpen size={15} weight="duotone" />
                            <span>{course.materialsCount} <span style={{ color: '#94a3b8', fontWeight: 'normal' }}>học liệu</span></span>
                          </div>
                          <div className="stat-item stat-item-questions">
                            <Question size={15} weight="duotone" />
                            <span>{course.questionsCount} <span style={{ color: '#94a3b8', fontWeight: 'normal' }}>câu hỏi</span></span>
                          </div>
                        </div>

                        {/* Nút Xem chi tiết */}
                        <button
                          onClick={() => navigate(`/courses/${course.id}`)}
                          className="btn-course-detail"
                        >
                          Xem chi tiết <ArrowRight size={14} weight="bold" />
                        </button>
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
                  <div>Cập nhật cuối</div>
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
                    <div>
                      <div className="table-time">
                        {course.updated_at ? formatDate(course.updated_at) : '—'}
                      </div>
                    </div>
                    <div className="table-arrow-cell">
                      <button
                        className="btn-table-detail"
                        onClick={(e) => { e.stopPropagation(); navigate(`/courses/${course.id}`); }}
                      >
                        Xem chi tiết <ArrowRight size={13} weight="bold" />
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
    </motion.div>
  );
};
