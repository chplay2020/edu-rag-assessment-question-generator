import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface ChartData {
  name: string;
  value: number;
}

export interface DashboardSummary {
  total_courses: number;
  total_materials: number;
  total_jobs: number;
  total_generated_questions: number;
  total_approved_questions: number;
  total_rejected_questions: number;
  validation_avg_score: number;
  questions_by_difficulty: ChartData[];
  questions_by_bloom: ChartData[];
  questions_by_status: ChartData[];
}

export const getDashboardSummary = async (): Promise<DashboardSummary> => {
  const token = localStorage.getItem('access_token');
  const response = await axios.get(`${API_URL}/dashboard/summary`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  return response.data;
};
