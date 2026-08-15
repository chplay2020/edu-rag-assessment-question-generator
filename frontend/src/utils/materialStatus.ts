
export type MaterialStatus = 'uploaded' | 'processing' | 'processed' | 'failed';
export type JobStatus = 'pending' | 'running' | 'done' | 'failed';

interface StatusMeta {
  label: string;
  modifier: string;
}

// Mapper trạng thái material → tiếng Việt
const MATERIAL_STATUS_MAP: Record<string, StatusMeta> = {
  uploaded:   { label: 'Chưa xử lý',     modifier: 'uploaded' },
  processing: { label: 'Đang xử lý',     modifier: 'processing' },
  processed:  { label: 'Đã xử lý',       modifier: 'processed' },
  failed:     { label: 'Xử lý thất bại', modifier: 'failed' },
};

// Mapper trạng thái job → tiếng Việt
const JOB_STATUS_MAP: Record<string, StatusMeta> = {
  pending: { label: 'Đang chờ',    modifier: 'processing' },
  running: { label: 'Đang xử lý', modifier: 'processing' },
  done:    { label: 'Hoàn thành', modifier: 'processed' },
  failed:  { label: 'Thất bại',   modifier: 'failed' },
};

const FALLBACK: StatusMeta = { label: 'Chưa xác định', modifier: 'unknown' };

export function getMaterialStatusMeta(status: string): StatusMeta {
  return MATERIAL_STATUS_MAP[status] ?? FALLBACK;
}

export function getJobStatusMeta(status: string): StatusMeta {
  return JOB_STATUS_MAP[status] ?? FALLBACK;
}

export function getMaterialStatusLabel(status: string): string {
  return getMaterialStatusMeta(status).label;
}

export function getJobStatusLabel(status: string): string {
  return getJobStatusMeta(status).label;
}

export function getMaterialStatusClass(prefix: string, status: string): string {
  const { modifier } = getMaterialStatusMeta(status);
  return `${prefix}-${modifier}`;
}
