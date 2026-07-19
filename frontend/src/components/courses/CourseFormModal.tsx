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

// Payload chỉ gồm các field backend nhận: title, code, description.
// Các field UI-only (instructor, materialsCount, ...) không gửi lên API.
export interface CourseFormPayload {
  title: string;
  code: string;
  description: string;
  instructor: string;
}

interface CourseFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: CourseFormPayload) => Promise<void>;
  course: Course | null;
  existingCourses: Course[];
  isSubmitting?: boolean;
  submitError?: string | null;
}

export const CourseFormModal: React.FC<CourseFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  course,
  existingCourses,
  isSubmitting = false,
  submitError = null,
}) => {
  const [code, setCode] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [instructor, setInstructor] = useState('');

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
      } else {
        setCode('');
        setTitle('');
        setDescription('');
        setInstructor('');
      }
      setErrors({});
    }
  }, [isOpen, course]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
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

    // Gọi async handler ở parent – parent xử lý API, đóng modal, hoặc set lỗi
    await onSubmit({
      code: trimmedCode,
      title: trimmedTitle,
      description: trimmedDescription,
      instructor: instructor.trim(),
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
    <div className="modal-backdrop" onClick={isSubmitting ? undefined : onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-header-title-area">
            <h3>{course ? 'Sửa môn học' : 'Thêm môn học'}</h3>
            <p className="modal-header-subtitle">
              {course ? 'Cập nhật thông tin môn học.' : 'Nhập thông tin để tạo môn học mới.'}
            </p>
          </div>
          <button
            className="btn-close"
            onClick={onClose}
            aria-label="Đóng"
            disabled={isSubmitting}
          >
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
                  disabled={isSubmitting}
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
                  disabled={isSubmitting}
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
                disabled={isSubmitting}
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
                  disabled={isSubmitting}
                />
              </div>
            </div>
          </div>

          <div className="modal-footer">
            {/* Hiển thị lỗi API nếu có */}
            {submitError && (
              <p className="modal-submit-error" role="alert">
                {submitError}
              </p>
            )}
            <Button variant="secondary" size="md" type="button" onClick={onClose} disabled={isSubmitting}>
              Hủy
            </Button>
            <Button variant="primary" size="md" type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Đang lưu...' : (course ? 'Lưu thay đổi' : 'Tạo môn học')}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
