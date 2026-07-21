/* Auth/RBAC thật chờ T010/T011 – backend hiện mock current_user_id = 1, role = "admin" */

import axios from 'axios';

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 8000,
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

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
  status?: 'active' | 'inactive';
}

export function mapApiCourse(raw: CourseApiResponse): Course {
  return {
    id: raw.id,
    title: raw.title,
    code: raw.code ?? '',
    description: raw.description ?? '',
    updated_at: raw.updated_at ?? raw.created_at,
    status: 'active',
    materialsCount: 0,
    questionsCount: 0,
    instructor: 'Chưa cập nhật',
  };
}

// API Helpers
// Lấy toàn bộ danh sách môn học từ backend.
// Trả về mảng Course hoặc ném lỗi (caller tự xử lý fallback).

export async function fetchCourses(): Promise<Course[]> {
  const res = await apiClient.get<CourseApiResponse[]>(`/api/v1/courses`);

  if (!Array.isArray(res.data)) {
    throw new Error('Invalid response format from GET /api/v1/courses');
  }

  return res.data.map(mapApiCourse);
}

// Lấy thông tin chi tiết của một môn học theo id.
// Trả về Course, hoặc null nếu 404, hoặc ném lỗi cho các trường hợp khác.

export async function fetchCourseById(id: number): Promise<Course | null> {
  try {
    const res = await apiClient.get<CourseApiResponse>(`/api/v1/courses/${id}`);
    return mapApiCourse(res.data);
  } catch (err) {
    if (axios.isAxiosError(err) && err.response?.status === 404) {
      return null;
    }
    throw err;
  }
}

// Payload gửi lên khi tạo/sửa môn học.
// Backend chỉ nhận title, code, description – các field khác (instructor, semester) là placeholder local.
export interface CourseCreatePayload {
  title: string;
  code?: string | null;
  description?: string | null;
}

export interface CourseUpdatePayload {
  title?: string | null;
  code?: string | null;
  description?: string | null;
}

// Tạo môn học mới
export async function createCourse(payload: CourseCreatePayload): Promise<Course> {
  const res = await apiClient.post<CourseApiResponse>(`/api/v1/courses`, payload);
  return mapApiCourse(res.data);
}

// Cập nhật môn học
export async function updateCourse(id: number, payload: CourseUpdatePayload): Promise<Course> {
  const res = await apiClient.put<CourseApiResponse>(`/api/v1/courses/${id}`, payload);
  return mapApiCourse(res.data);
}

// Xóa môn học (soft delete)
export async function deleteCourse(id: number): Promise<void> {
  await apiClient.delete(`/api/v1/courses/${id}`);
}
