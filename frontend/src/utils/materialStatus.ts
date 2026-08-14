
export type MaterialStatus = 'uploaded' | 'processing' | 'processed' | 'failed';

interface StatusMeta {

  label: string;
  modifier: string;
}

const STATUS_MAP: Record<string, StatusMeta> = {
  uploaded: { label: 'Đã tải lên', modifier: 'uploaded' },
  processing: { label: 'Đang xử lý', modifier: 'processing' },
  processed: { label: 'Đã xử lý', modifier: 'processed' },
  failed: { label: 'Xử lý thất bại', modifier: 'failed' },
};

const FALLBACK: StatusMeta = { label: 'Chưa xác định', modifier: 'unknown' };

export function getMaterialStatusMeta(status: string): StatusMeta {
  return STATUS_MAP[status] ?? FALLBACK;
}


export function getMaterialStatusLabel(status: string): string {
  return getMaterialStatusMeta(status).label;
}

export function getMaterialStatusClass(prefix: string, status: string): string {
  const { modifier } = getMaterialStatusMeta(status);
  return `${prefix}-${modifier}`;
}
