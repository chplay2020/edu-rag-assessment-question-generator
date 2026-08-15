// Types
export type ProcessingStatus = 'pending' | 'processing' | 'done' | 'failed';

export interface MockProcessingState {
  materialId: number;
  status: ProcessingStatus;
  startedAt: number | null;
  completedAt: number | null;
  failureReason: string | null;
  chunkCount: number;
  extractedTextPreview: string | null;
}

export interface MockProcessOptions {
  simulateFailure?: boolean;
}

// Constants

const MOCK_STATE_MAP = new Map<number, MockProcessingState>();
const SESSION_KEY_PREFIX = '__mock_processing_t029_';

const MOCK_PREVIEW_TEXT = `Chương 1: Giới thiệu tổng quan về Học máy trong Giáo dục

Tài liệu này trình bày các khái niệm cơ bản về học máy và trí tuệ nhân tạo ứng dụng \
trong lĩnh vực giáo dục. Các phương pháp hiện đại như RAG (Retrieval-Augmented Generation) \
đang được ứng dụng rộng rãi để cải thiện chất lượng câu hỏi kiểm tra tự động.

Chương 2: Phương pháp Nhúng Vector và Truy xuất Ngữ nghĩa

Hệ thống sử dụng vector embedding để lưu trữ và truy xuất nội dung tài liệu một cách hiệu \
quả. Mỗi đoạn văn bản (chunk) được mã hóa thành vector và lưu trong cơ sở dữ liệu pgvector \
để hỗ trợ tìm kiếm ngữ nghĩa nhanh và chính xác.

Chương 3: Quy trình Tạo Câu hỏi Tự động

Từ nội dung tài liệu đã được xử lý, hệ thống có thể tự động tạo ra các câu hỏi kiểm tra \
ở nhiều mức độ khó khác nhau: nhớ, hiểu, áp dụng, phân tích, đánh giá và sáng tạo.


⚠️  [MOCK UI – T029] Nội dung này chỉ dùng để kiểm tra giao diện.
     Không phải dữ liệu thật. Sẽ được thay bằng dữ liệu API sau khi T028 hoàn thành.`;

const MOCK_FAILURE_REASON =
  'Không thể xử lý tài liệu này. Tệp có thể bị lỗi, được bảo vệ bằng mật khẩu hoặc không chứa nội dung có thể trích xuất. Vui lòng kiểm tra tệp và thử lại.';

// Internal helpers
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function randomDelay(min = 3000, max = 5000): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function saveToSession(state: MockProcessingState): void {
  try {
    sessionStorage.setItem(
      SESSION_KEY_PREFIX + state.materialId,
      JSON.stringify(state),
    );
  } catch {

  }
}

function loadFromSession(materialId: number): MockProcessingState | null {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY_PREFIX + materialId);
    return raw ? (JSON.parse(raw) as MockProcessingState) : null;
  } catch {
    return null;
  }
}

function persistState(state: MockProcessingState): void {
  MOCK_STATE_MAP.set(state.materialId, state);
  saveToSession(state);
}

// Public API
export function getMockState(materialId: number): MockProcessingState | null {
  return MOCK_STATE_MAP.get(materialId) ?? loadFromSession(materialId) ?? null;
}

export function resetMockState(materialId: number): void {
  MOCK_STATE_MAP.delete(materialId);
  try {
    sessionStorage.removeItem(SESSION_KEY_PREFIX + materialId);
  } catch {
  }
}

export function resetAllMockStates(): void {
  MOCK_STATE_MAP.clear();
  try {
    const keys: string[] = [];
    for (let i = 0; i < sessionStorage.length; i++) {
      const k = sessionStorage.key(i);
      if (k?.startsWith(SESSION_KEY_PREFIX)) keys.push(k);
    }
    keys.forEach((k) => sessionStorage.removeItem(k));
  } catch {

  }
}

export async function mockProcessMaterial(
  materialId: number,
  options: MockProcessOptions = {},
  onTransition?: (state: MockProcessingState) => void,
): Promise<MockProcessingState> {
  const { simulateFailure = false } = options;

  // 1. pending
  const pendingState: MockProcessingState = {
    materialId,
    status: 'pending',
    startedAt: null,
    completedAt: null,
    failureReason: null,
    chunkCount: 0,
    extractedTextPreview: null,
  };
  persistState(pendingState);
  onTransition?.(pendingState);

  await sleep(400);

  // 2. processing
  const processingState: MockProcessingState = {
    ...pendingState,
    status: 'processing',
    startedAt: Date.now(),
  };
  persistState(processingState);
  onTransition?.(processingState);

  await sleep(randomDelay(3000, 5000));

  // 3. done | failed
  const finalState: MockProcessingState = simulateFailure
    ? {
      ...processingState,
      status: 'failed',
      completedAt: Date.now(),
      failureReason: MOCK_FAILURE_REASON,
    }
    : {
      ...processingState,
      status: 'done',
      completedAt: Date.now(),
      chunkCount: Math.floor(Math.random() * 20) + 5, // 5–24 chunks
      extractedTextPreview: MOCK_PREVIEW_TEXT,
    };

  persistState(finalState);
  onTransition?.(finalState);

  return finalState;
}
