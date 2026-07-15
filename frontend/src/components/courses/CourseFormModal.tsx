import React, { useState, useEffect } from 'react';
import { X } from '@phosphor-icons/react';
import { Button } from '../common/Button';
import './CourseFormModal.css';

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
  status?: 'active' | 'inactive';
}

interface CourseFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (courseData: Omit<Course, 'materialsCount' | 'questionsCount'>) => void;
  course: Course | null;
  existingCourses: Course[];
}

export const CourseFormModal: React.FC<CourseFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  course,
  existingCourses,
}) => {
  const [code, setCode] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [instructor, setInstructor] = useState('');
  const [semester, setSemester] = useState('');
  
  const [errors, setErrors] = useState<{
    code?: string;
    title?: string;
    description?: string;
  }>({});

  useEffect(() => {
    if (isOpen) {
      if (course) {
        setCode(course.code || '');
        setTitle(course.title || '');
        setDescription(course.description || '');
        setInstructor(course.instructor || '');
        setSemester(course.semester || '');
      } else {
        setCode('');
        setTitle('');
        setDescription('');
        setInstructor('');
        setSemester('');
      }
      setErrors({});
    }
  }, [isOpen, course]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors: typeof errors = {};
    const trimmedCode = code.trim();
    const trimmedTitle = title.trim();
    const trimmedDescription = description.trim();

    if (!trimmedCode) {
      newErrors.code = 'Mã môn học là bắt buộc';
    } else {
      const isDuplicate = existingCourses.some(
        (c) => c.code.trim().toLowerCase() === trimmedCode.toLowerCase() && (!course || c.id !== course.id)
      );
      if (isDuplicate) {
        newErrors.code = 'Mã môn học này đã tồn tại';
      }
    }
    
    if (!trimmedTitle) {
      newErrors.title = 'Tên môn học là bắt buộc';
    }
    
    if (!trimmedDescription) {
      newErrors.description = 'Mô tả môn học là bắt buộc';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onSubmit({
      id: course ? course.id : 0,
      code: trimmedCode,
      title: trimmedTitle,
      description: trimmedDescription,
      instructor: instructor.trim(),
      semester: semester.trim(),
      status: course?.status || 'active', // Giữ nguyên trạng thái cũ hoặc mặc định là active ngầm
      updated_at: new Date().toISOString(),
    });
  };

  const handleFieldChange = (field: 'code' | 'title' | 'description', value: string) => {
    if (field === 'code') setCode(value);
    if (field === 'title') setTitle(value);
    if (field === 'description') setDescription(value);

    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title-area">
            <h3>{course ? 'Sửa môn học' : 'Thêm môn học'}</h3>
            <p className="modal-header-subtitle">
              {course ? 'Cập nhật thông tin môn học.' : 'Nhập thông tin để tạo môn học mới.'}
            </p>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Đóng">
            <X size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="modal-form">
          <div className="modal-body-scroll">
            <div className="form-row">
              <div className="form-group flex-1">
                <label htmlFor="course-code" className="required-field">Mã môn học</label>
                <input
                  id="course-code"
                  type="text"
                  className={`form-input ${errors.code ? 'input-error' : ''}`}
                  placeholder="Ví dụ: INT3306"
                  value={code}
                  onChange={(e) => handleFieldChange('code', e.target.value)}
                />
                {errors.code && <span className="error-text">{errors.code}</span>}
              </div>

              <div className="form-group flex-2">
                <label htmlFor="course-title" className="required-field">Tên môn học</label>
                <input
                  id="course-title"
                  type="text"
                  className={`form-input ${errors.title ? 'input-error' : ''}`}
                  placeholder="Ví dụ: Lập trình Web nâng cao"
                  value={title}
                  onChange={(e) => handleFieldChange('title', e.target.value)}
                />
                {errors.title && <span className="error-text">{errors.title}</span>}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="course-description" className="required-field">Mô tả môn học</label>
              <textarea
                id="course-description"
                className={`form-textarea ${errors.description ? 'input-error' : ''}`}
                placeholder="Nhập mô tả ngắn gọn về môn học..."
                value={description}
                rows={3}
                onChange={(e) => handleFieldChange('description', e.target.value)}
              />
              {errors.description && <span className="error-text">{errors.description}</span>}
            </div>

            <div className="form-row">
              <div className="form-group flex-1">
                <label htmlFor="course-instructor">Giảng viên phụ trách</label>
                <input
                  id="course-instructor"
                  type="text"
                  className="form-input"
                  placeholder="Ví dụ: TS. Nguyễn Văn An"
                  value={instructor}
                  onChange={(e) => setInstructor(e.target.value)}
                />
              </div>
              <div className="form-group flex-1">
                <label htmlFor="course-semester">Học kỳ</label>
                <input
                  id="course-semester"
                  type="text"
                  className="form-input"
                  placeholder="Ví dụ: Học kỳ 2 – 2025-2026"
                  value={semester}
                  onChange={(e) => setSemester(e.target.value)}
                />
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <Button variant="secondary" size="md" type="button" onClick={onClose}>
              Hủy
            </Button>
            <Button variant="primary" size="md" type="submit">
              {course ? 'Lưu thay đổi' : 'Tạo môn học'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
