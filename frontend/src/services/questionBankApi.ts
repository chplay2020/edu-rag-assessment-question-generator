import { apiClient } from './courseApi';
import type { QuestionResponse } from './jobApi';

export interface QuestionBankParams {
  course_id?: number;
  difficulty?: string;
  bloom_level?: string;
  question_type?: string;
  skip?: number;
  limit?: number;
}

export async function getQuestionBank(params?: QuestionBankParams): Promise<QuestionResponse[]> {
  const res = await apiClient.get<QuestionResponse[]>('/questions/bank', { params });
  return res.data;
}
