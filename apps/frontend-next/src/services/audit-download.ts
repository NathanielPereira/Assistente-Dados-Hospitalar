/**
 * Downloads audit export file
 * @param sessionId - Session ID to filter exports (optional)
 * @param format - Export format: 'csv' or 'json'
 */
export async function downloadAuditExport(sessionId: string, format: 'csv' | 'json'): Promise<void> {
  const url = `/api/v1/audit/exports?session_id=${encodeURIComponent(sessionId)}&format=${format}`;
  const response = await fetch(url);
  const blob = await response.blob();
  const objectUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = objectUrl;
  a.download = `audit-export-${sessionId || 'all'}.${format}`;
  a.click();
  window.URL.revokeObjectURL(objectUrl);
}
