import { apiClient } from './courseApi';

// Types
export interface Material {
  id: number;
  title: string;
  course_id: number;
  uploaded_by: number;
  file_url: string;
  status: string;
  created_at: string;
}

// định dạng file cho phép
export const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt'];
export const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
];
export const MAX_FILE_SIZE_MB = 10;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export function validateFile(file: File): string | null {
  const nameParts = file.name.split('.');
  const ext = nameParts.length > 1 ? '.' + nameParts.pop()!.toLowerCase() : '';
  const isMimeOk = ALLOWED_MIME_TYPES.includes(file.type);
  const isExtOk = ALLOWED_EXTENSIONS.includes(ext);

  if (!isMimeOk && !isExtOk) {
    return `Định dạng file không hợp lệ. Chỉ chấp nhận: PDF, DOCX hoặc TXT.`;
  }
  if (file.size > MAX_FILE_SIZE_BYTES) {
    const sizeMB = (file.size / 1024 / 1024).toFixed(1);
    return `File quá lớn (${sizeMB} MB). Giới hạn tối đa là ${MAX_FILE_SIZE_MB} MB.`;
  }
  return null;
}

// API helpers
export async function uploadMaterial(courseId: number, file: File): Promise<Material> {
  const formData = new FormData();
  formData.append('course_id', String(courseId));
  formData.append('file', file);

  const res = await apiClient.post<Material>('/materials/upload', formData);
  return res.data;
}

// lấy danh sách tài liệu theo ID khóa học
export async function getMaterialsByCourse(courseId: number): Promise<Material[]> {
  const res = await apiClient.get<Material[]>(`/materials/course/${courseId}`);
  if (!Array.isArray(res.data)) return [];
  return res.data;
}

// cảnh báo lỗi API
export function extractApiError(err: unknown): string {
  const axiosErr = err as {
    response?: {
      data?: { message?: string; detail?: unknown };
      status?: number;
    };
  };

  const data = axiosErr?.response?.data;
  const status = axiosErr?.response?.status;

  // lấy thông báo lỗi từ API
  if (typeof data?.message === 'string' && data.message) return data.message;
  if (data?.detail) {
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) return 'Dữ liệu gửi lên không hợp lệ. Vui lòng kiểm tra lại.';
  }

  switch (status) {
    case 401: return 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.';
    case 403: return 'Bạn không có quyền thực hiện hành động này.';
    case 404: return 'Môn học không tồn tại hoặc đã bị xóa.';
    case 413: return 'File quá lớn. Vui lòng chọn file nhỏ hơn 10 MB.';
    case 415: return 'Định dạng file không được hỗ trợ. Chỉ chấp nhận PDF, DOCX, TXT.';
    case 422: return 'Dữ liệu không hợp lệ. Vui lòng kiểm tra file và thử lại.';
  }

  if (status && status >= 500) return 'Lỗi máy chủ. Vui lòng thử lại sau ít phút.';
  return 'Đã xảy ra lỗi không xác định. Vui lòng thử lại.';
}

// định dạng ngày tháng
export function formatViDate(isoString: string): string {
  try {
    const date = new Date(isoString);
    const datePart = date.toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
    const timePart = date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
    return `${datePart} lúc ${timePart}`;
  } catch {
    return isoString;
  }
}


// định dạng dung lượng file
export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

// lấy URL tải xuống đầy đủ (gắn backend domain)
export function getMaterialDownloadUrl(fileUrl: string): string {
  if (!fileUrl) return '#';
  if (fileUrl.startsWith('http')) return fileUrl;

  const baseUrl = (import.meta.env.VITE_API_URL as string | undefined) || 'http://localhost:8000/api/v1';
  // Xóa đuôi /api/v1 để lấy root domain của backend (http://localhost:8000)
  const backendRoot = baseUrl.replace(/\/api\/v1\/?$/, '');

  return `${backendRoot}${fileUrl.startsWith('/') ? '' : '/'}${fileUrl}`;
}

// Material Detail Types
export interface MaterialDetail extends Material {
  chunk_count: number;
  extracted_text_preview: string | null;
}

// lấy thông tin chi tiết tài liệu
export async function getMaterialById(materialId: number): Promise<MaterialDetail> {
  const res = await apiClient.get<MaterialDetail>(`/materials/${materialId}`);
  return res.data;
}

// helper để tải xuống
export function downloadMaterialFile(fileUrl: string, filename: string): void {
  const url = getMaterialDownloadUrl(fileUrl);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename || 'download';
  // target blank for cross-origin downloads
  link.target = '_blank';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
