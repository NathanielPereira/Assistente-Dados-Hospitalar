export async function downloadAuditExport(sessionId: string, format: 'csv' | 'json'): Promise<void> {
  const response = await fetch(/api/v1/audit/exports?session_id=&format=);
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = udit-.;
  a.click();
  window.URL.revokeObjectURL(url);
}
