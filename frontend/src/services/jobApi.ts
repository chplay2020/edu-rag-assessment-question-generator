import { apiClient } from './courseApi';
import type { MaterialDetail } from './materialApi';

// Types cho Job và Questions
export interface JobConfig {
  query?: string;
  number_of_questions: number;
  difficulty: string;
  bloom_level?: string;
  language: string;
  top_k: number;
}

export interface JobResponse {
  id: number;
  material_id: number;
  task_type: string;
  status: 'pending' | 'running' | 'done' | 'failed';
  percent?: number;
  created_at: string;
  started_at?: string;
  finished_at?: string;
  error_message?: string;
  config?: JobConfig;
  material?: MaterialDetail;
}

export interface Option {
  id: number;
  content: string;
  is_correct: boolean;
}

export interface QuestionValidationResultResponse {
  id: number;
  validator_type: string;
  score?: Record<string, number>;
  warnings?: string[];
}

export interface QuestionResponse {
  id: number;
  job_id: number;
  content: string;
  difficulty: string;
  bloom_level: string;
  question_type: string;
  explanation: string;
  options: Option[];
  source_chunk_ids: number[];
  status: string;
  created_at: string;
  validation_results?: QuestionValidationResultResponse[];
}

/**
 * Gọi API tạo Job sinh câu hỏi
 */
export async function createQuestionGenerationJob(materialId: number, config: JobConfig): Promise<JobResponse> {
  const res = await apiClient.post<JobResponse>(`/jobs/material/${materialId}/generate-questions`, config);
  return res.data;
}

/**
 * Lấy trạng thái của một Job
 */
export async function getJobStatus(jobId: number): Promise<JobResponse> {
  const res = await apiClient.get<JobResponse>(`/jobs/${jobId}`);
  return res.data;
}

/**
 * Lấy danh sách câu hỏi đã được sinh ra từ Job
 */
export async function getJobQuestions(jobId: number): Promise<QuestionResponse[]> {
  const res = await apiClient.get<QuestionResponse[]>(`/jobs/${jobId}/questions`);
  return res.data;
}

/**
 * Cập nhật nội dung câu hỏi 
 */
export async function updateQuestion(questionId: number, data: {
  content?: string;
  explanation?: string;
  difficulty?: string;
  bloom_level?: string;
  options?: Array<{ id: number; content: string; is_correct: boolean }>;
}): Promise<QuestionResponse> {
  const res = await apiClient.put<QuestionResponse>(`/questions/${questionId}`, data);
  return res.data;
}

/**
 * Duyệt hoặc từ chối câu hỏi 
 */
export async function reviewQuestion(questionId: number, status: 'approved' | 'rejected'): Promise<any> {
  const res = await apiClient.post(`/questions/${questionId}/review`, { status });
  return res.data;
}

