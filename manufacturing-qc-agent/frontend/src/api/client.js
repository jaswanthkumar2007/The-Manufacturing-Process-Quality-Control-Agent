/**
 * Axios API client — all calls to the FastAPI backend.
 */
import axios from 'axios';

const BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Sensors ──────────────────────────────────────────────────────────────────
export const getLatestReadings       = ()                          => api.get('/sensors/latest');
export const getLatestForLine        = (line)                      => api.get(`/sensors/latest/${line}`);
export const getSensorHistory        = (params)                    => api.get('/sensors/history', { params });
export const getAnomalyReadings      = (hours = 24)                => api.get('/sensors/anomalies', { params: { hours } });
export const getThresholds           = ()                          => api.get('/sensors/thresholds');
export const getProcessLines         = ()                          => api.get('/sensors/process-lines');
export const getControlChart         = (line, sensor)              => api.get(`/sensors/control-chart/${line}/${sensor}`);

// ── Analysis ─────────────────────────────────────────────────────────────────
export const getDashboardSummary     = ()                          => api.get('/analysis/dashboard-summary');
export const getQualityStats         = (hours = 24)                => api.get('/analysis/quality-stats', { params: { hours } });
export const predictQuality          = (line)                      => api.get(`/analysis/predict/${line}`);
export const checkAnomaly            = (line)                      => api.get(`/analysis/anomaly-check/${line}`);
export const getAlerts               = ()                          => api.get('/analysis/alerts');
export const resolveAlert            = (id)                        => api.post(`/analysis/alerts/${id}/resolve`);

// ── Agents ───────────────────────────────────────────────────────────────────
export const chatWithAgent           = (data)                      => api.post('/agents/chat', data);
export const getChatHistory          = (sessionId)                 => api.get(`/agents/history/${sessionId}`);
export const getAgentStatus          = ()                          => api.get('/agents/status');

// ── Reports ──────────────────────────────────────────────────────────────────
export const generateReport          = (data)                      => api.post('/reports/generate', data);
export const listReports             = ()                          => api.get('/reports/');

// ── Knowledge ────────────────────────────────────────────────────────────────
export const listDocuments           = ()                          => api.get('/knowledge/documents');
export const getDocument             = (id)                        => api.get(`/knowledge/documents/${id}`);
export const askKnowledgeBase        = (question)                  => api.post('/knowledge/ask', { question });

export default api;
