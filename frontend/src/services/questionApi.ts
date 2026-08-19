import { apiClient } from './courseApi';
import type { QuestionResponse } from './jobApi';

export interface QuestionUpdate {
  content?: string;
  difficulty?: string;
  bloom_level?: string;
  question_type?: string;
  explanation?: string;
  status?: string;
  options?: { content: string; is_correct: boolean }[];
}

export interface ReviewCreate {
  status: 'approved' | 'rejected';
  feedback?: string;
}

export async function getAllQuestions(params?: { course_id?: number; job_id?: number; status?: string }): Promise<QuestionResponse[]> {
  const res = await apiClient.get<QuestionResponse[]>('/questions', { params });
  return res.data;
}

export async function updateQuestion(questionId: number, data: QuestionUpdate): Promise<QuestionResponse> {
  const res = await apiClient.put<QuestionResponse>(`/questions/${questionId}`, data);
  return res.data;
}

export async function reviewQuestion(questionId: number, data: ReviewCreate): Promise<any> {
  const res = await apiClient.post(`/questions/${questionId}/review`, data);
  return res.data;
}
