import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const assessUseCase = async (useCaseData) => {
  const response = await api.post('/assess', useCaseData);
  return response.data;
};

export const getAssessments = async () => {
  const response = await api.get('/assessments');
  return response.data;
};



export const getDocuments = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export const ingestDocuments = async () => {
  const response = await api.post('/documents/ingest');
  return response.data;
};

export const downloadPdfReport = async (assessmentId, useCaseTitle) => {
  const response = await api.post(
    '/reports/generate-pdf',
    { assessment_id: assessmentId },
    { responseType: 'blob' }
  );

  // Build filename
  const titlePart = (useCaseTitle || 'report')
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s-]+/g, '_')
    .toLowerCase()
    .substring(0, 60);
  const datePart = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const filename = `ai_governance_report_${titlePart}_${datePart}.pdf`;

  // Trigger browser download
  const blob = new Blob([response.data], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
