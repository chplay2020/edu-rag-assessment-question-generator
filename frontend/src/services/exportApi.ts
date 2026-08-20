import api from './api';

const sanitizeFilename = (name: string): string => {
  return name
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, '')
    .replace(/^\.+|\.+$/g, '')
    .trim();
};

export const exportExcel = async (questionIds: number[]): Promise<{ blob: Blob; filename: string }> => {
  const response = await api.post(
    '/exports/excel',
    { question_ids: questionIds },
    { responseType: 'blob' }
  );

  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, '0');
  const ts = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  let filename = `questions_export_${ts}.xlsx`;

  const disposition = response.headers['content-disposition'];
  if (disposition) {
    let parsedName = '';

    const utf8Regex = /filename\*=UTF-8''([^;]+)/i;
    const utf8Match = utf8Regex.exec(disposition);
    if (utf8Match && utf8Match[1]) {
      try {
        parsedName = decodeURIComponent(utf8Match[1]);
      } catch {

      }
    }

    if (!parsedName) {
      const asciiRegex = /filename="([^"]+)"|filename=([^;]+)/i;
      const asciiMatch = asciiRegex.exec(disposition);
      if (asciiMatch) {
        parsedName = asciiMatch[1] || asciiMatch[2];
      }
    }

    if (parsedName) {
      const safeName = sanitizeFilename(parsedName);
      if (safeName && safeName.length > 0) {
        filename = safeName;
      }
    }
  }

  if (!filename.toLowerCase().endsWith('.xlsx')) {
    filename += '.xlsx';
  }

  return { blob: response.data, filename };
};

export const formatApiErrorDetail = (detail: unknown): string => {
  if (typeof detail === 'string') return detail.trim();

  if (Array.isArray(detail)) {
    const messages = detail.map((err) => {
      let fieldStr = '';
      if (err.loc && Array.isArray(err.loc) && err.loc.length > 0) {
        fieldStr = ` (${err.loc[err.loc.length - 1]})`;
      }
      return `${err.msg || 'Lỗi dữ liệu'}${fieldStr}`;
    });
    return messages.join(', ');
  }

  if (detail && typeof detail === 'object') {
    const d = detail as Record<string, unknown>;
    if (typeof d.message === 'string') return d.message;
    if (typeof d.msg === 'string') return d.msg;
    if (typeof d.detail === 'string') return d.detail;
  }

  return 'Không thể xuất file Excel. Vui lòng thử lại.';
};
