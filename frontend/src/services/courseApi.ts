/* Auth/RBAC thật chờ T010/T011 – backend hiện mock current_user_id = 1, role = "admin" */

import axios from 'axios';

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) || 'http://localhost:8000';

export interface CourseApiResponse {
  id: number;
  title: string;
  code: string | null;
  description: string | null;
  created_by: number;
  created_at: string;
  updated_at: string | null;
  is_deleted: boolean;
}

export interface Course {
  id: number;
  title: string;
  code: string;
  description: string;
  materialsCount?: number;  // Placeholder – backend chưa có, chờ Material API
  questionsCount?: number;  // Placeholder – backend chưa có, chờ Question API
  updated_at?: string | null;
  instructor?: string;      // Placeholder – backend chưa có
  semester?: string;        // Placeholder – backend chưa có
  status?: 'active' | 'inactive';
}

// Mock Lookup (dùng để giữ số liệu demo khi id trùng) 
const MOCK_EXTRAS: Record<number, Pick<Course, 'materialsCount' | 'questionsCount' | 'instructor' | 'semester'>> = {
  1: { materialsCount: 12, questionsCount: 160, instructor: 'TS. Nguyễn Văn An', semester: 'Học kỳ 2 – 2025-2026' },
  2: { materialsCount: 8, questionsCount: 120, instructor: 'PGS. Trần Thị Bình', semester: 'Học kỳ 2 – 2025-2026' },
  3: { materialsCount: 15, questionsCount: 240, instructor: 'GS. Lê Hoàng Cường', semester: 'Học kỳ 1 – 2025-2026' },
  4: { materialsCount: 10, questionsCount: 150, instructor: 'TS. Phạm Minh Đức', semester: 'Học kỳ 1 – 2025-2026' },
};

// Chuyển đổi CourseApiResponse (backend) → Course (frontend).
// Các field chưa có từ backend (materialsCount, questionsCount, instructor, semester)

export function mapApiCourse(raw: CourseApiResponse): Course {
  const extras = MOCK_EXTRAS[raw.id] ?? {
    materialsCount: 0,
    questionsCount: 0,
    instructor: 'Giảng viên phụ trách',
    semester: 'Học kỳ hiện tại',
  };

  return {
    id: raw.id,
    title: raw.title,
    code: raw.code ?? '',
    description: raw.description ?? '',
    updated_at: raw.updated_at ?? raw.created_at,
    status: 'active',
    ...extras,
  };
}

// API Helpers
// Lấy toàn bộ danh sách môn học từ backend.
// Trả về mảng Course hoặc ném lỗi (caller tự xử lý fallback).

export async function fetchCourses(): Promise<Course[]> {
  const res = await axios.get<CourseApiResponse[]>(`${BASE_URL}/api/v1/courses`, {
    timeout: 8000,
  });

  if (!Array.isArray(res.data)) {
    throw new Error('Invalid response format from GET /api/v1/courses');
  }

  return res.data.map(mapApiCourse);
}

// Lấy thông tin chi tiết của một môn học theo id.
// Trả về Course, hoặc null nếu 404, hoặc ném lỗi cho các trường hợp khác.

export async function fetchCourseById(id: number): Promise<Course | null> {
  try {
    const res = await axios.get<CourseApiResponse>(`${BASE_URL}/api/v1/courses/${id}`, {
      timeout: 8000,
    });
    return mapApiCourse(res.data);
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      return null;
    }
    throw err;
  }
}
