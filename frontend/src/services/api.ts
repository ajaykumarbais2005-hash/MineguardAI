import axios from 'axios'

export const AUTH_UNAUTHORIZED_EVENT = 'mineguard:unauthorized'

let accessToken: string | null = null

export function setAccessToken(token: string | null) {
  accessToken = token
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.set('Authorization', `Bearer ${accessToken}`)
  } else {
    config.headers.delete('Authorization')
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (
      axios.isAxiosError(error) &&
      error.response?.status === 401 &&
      !error.config?.url?.endsWith('/auth/login') &&
      typeof window !== 'undefined'
    ) {
      window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT))
    }
    return Promise.reject(error)
  },
)

export type TokenResponse = {
  access_token: string
  token_type: string
  expires_in: number
}

export type AuthUser = {
  id: number
  email: string
  full_name: string
  is_active: boolean
  role: string
  created_at: string
}

export type Mine = {
  id: number
  mine_name: string
  mine_code: string
  location: string
  state: string
  district: string
  mine_type: string
  operator: string
  production_capacity: number | null
  current_production: number | null
  status: string
  risk_level: string
  manager_id: number | null
  manager_name: string | null
  latitude: number | null
  longitude: number | null
  created_at: string
}

export type MineZone = { id: number; name: string; zone_type: string; status: string }
export type MineDetail = Mine & { zones: MineZone[]; statistics: { zone_count: number; inspection_count: number; open_violation_count: number; active_sensor_count: number; alert_count: number } }
export type ComplianceRequirement = { id: number; requirement_code: string; title: string; description: string; category: string; regulation_reference: string; mandatory: boolean; applicable_mine_type: string; frequency: string; status: string; last_verification: string | null; next_due_date: string | null }
export type ComplianceSummary = { compliant: number; partially_compliant: number; non_compliant: number; overdue: number; critical: number; total: number }
export type ChecklistItem = { id?: number; item_code: string; question: string; response: string | null; remarks: string | null }
export type Inspection = { id: number; inspection_code: string; mine_id: number; zone_id: number | null; inspector_id: number; checklist_name: string; status: string; findings: string | null; remarks: string | null; evidence_path: string | null; started_at: string; submitted_at: string | null; mine_name: string; zone_name: string | null; checklist_items: ChecklistItem[] }
export type Violation = { id: number; violation_code: string; mine_id: number; zone_id: number | null; inspection_id: number | null; category: string; description: string; severity: string; detected_at: string; detected_by: number; status: string; due_date: string | null; evidence_path: string | null; assigned_officer: string | null; mine_name: string; zone_name: string | null }
export type ViolationSummary = { open: number; assigned: number; in_progress: number; resolved: number; verified: number; closed: number; critical: number; total: number }
export type CAPA = { id: number; action_code: string; violation_id: number; description: string; responsible_person_id: number; contractor_id: number | null; priority: string; deadline: string; status: string; evidence_path: string | null; verification: string | null; closure_date: string | null; violation_code: string; contractor_name: string | null; responsible_person_name: string | null }
export type CAPASummary = { open: number; in_progress: number; submitted: number; verification_pending: number; verified: number; rejected: number; closed: number; total: number }
export type ContractorWorker = { id: number; worker_code: string; name: string; role: string; training_status: string; ppe_status: string; medical_valid_until: string | null; training_valid_until: string | null; site_assignment: string | null }
export type Contractor = { id: number; contractor_code: string; company_name: string; license_number: string; contact_person: string; phone: string; email: string; work_type: string; workers_count: number; compliance_score: number; risk_score: number; status: string; workers: ContractorWorker[] }
export type ContractorSummary = { total: number; active: number; average_compliance_score: number; workers: number; high_risk: number }
export type Alert = { id: number; alert_type: string; severity: string; message: string; mine_id: number; zone_id: number | null; status: string; acknowledged_by: string | null; created_at: string; mine_name: string; zone_name: string | null }
export type AlertSummary = { unread: number; acknowledged: number; resolved: number; critical: number; total: number }
export type AuditLog = { id: number; user_id: number | null; action: string; entity: string; entity_id: string | null; description: string; ip_address: string | null; created_at: string; user_name: string | null; user_email: string | null }
export type AuditSummary = { total: number; today: number; creates: number; updates: number; deletes: number }
export type PPEDetection = { label: string; confidence: number; present: boolean }
export type PPEWorkflow = { risk_event_id: number | null; violation_id: number | null; alert_id: number | null; capa_id: number | null; contractor_id: number | null; status: string }
export type PPEResult = { event_id: number; mode: string; event_type: string; severity: string; detections: PPEDetection[]; confidence: number; mine_id: number; zone_id: number | null; camera: string; created_at: string; disclaimer: string; workflow: PPEWorkflow | null }
export type RiskEvent = { id: number; mine_id: number; zone_id: number | null; event_type: string; score: number; level: string; severity: number; likelihood: number; exposure: number; recurrence: number; reason: string; recommended_action: string; created_at: string; mine_name: string; zone_name: string | null }
export type AnomalyResult = { id: number | null; mine_id: number; zone_id: number | null; metric: string; value: number; threshold: number; is_anomaly: boolean; severity: number; likelihood: number; exposure: number; recurrence: number; reason: string; risk_event_id: number | null; risk_score: number | null; risk_level: string | null; created_at: string; mode: string }
export type OCRResult = { id: number; extracted_text: string; confidence: number; detected_fields: string | null; verification_status: string; processed_at: string }
export type DocumentRecord = { id: number; file_name: string; document_type: string; file_path: string; mine_id: number | null; contractor_id: number | null; uploaded_by: number; uploaded_at: string; status: string; mine_name: string | null; contractor_name: string | null; ocr_result: OCRResult | null }
export type GISPoint = { id: string; kind: string; label: string; latitude: number; longitude: number; mine_id: number; zone_id: number | null; status: string | null; risk_level: string | null; severity: string | null; demo_position: boolean }
export type GISMapResponse = { points: GISPoint[]; mode: string }
export type IoTReading = { id: number; sensor_id: number; value: number; recorded_at: string; is_anomaly: boolean }
export type IoTSensor = { id: number; sensor_code: string; mine_id: number; zone_id: number | null; sensor_type: string; unit: string; threshold: number; status: string; last_reading: number | null; last_reading_at: string | null; mine_name: string; zone_name: string | null; readings: IoTReading[] }
export type IoTSimulation = { sensors: IoTSensor[]; alerts_created: number; mode: string }
export type ReportResponse = { report_type: string; mode: string; generated_at: string; rows: Array<Record<string, string | number | boolean | null>> }
export type WorkflowSummary = { ai_events: number; risk_events: number; open_violations: number; unread_alerts: number; open_capa: number }

export async function loginRequest(email: string, password: string) {
  const form = new URLSearchParams()
  form.set('username', email)
  form.set('password', password)
  const response = await api.post<TokenResponse>('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return response.data
}

export async function currentUserRequest() {
  const response = await api.get<AuthUser>('/auth/me')
  return response.data
}

export async function logoutRequest() {
  await api.post('/auth/logout')
}

export async function listMines(params: { search?: string; status?: string; risk_level?: string; sort_by?: string; descending?: boolean } = {}) {
  const response = await api.get<Mine[]>('/mines', { params })
  return response.data
}

export async function getMine(id: number) {
  const response = await api.get<MineDetail>(`/mines/${id}`)
  return response.data
}

export async function createMine(payload: Omit<Mine, 'id' | 'manager_name' | 'created_at'>) {
  const response = await api.post<Mine>('/mines', payload)
  return response.data
}

export async function updateMine(id: number, payload: Partial<Omit<Mine, 'id' | 'manager_name' | 'created_at'>>) {
  const response = await api.patch<Mine>(`/mines/${id}`, payload)
  return response.data
}

export async function deleteMine(id: number) {
  await api.delete(`/mines/${id}`)
}

export async function listCompliance(params: { search?: string; status?: string; category?: string } = {}) {
  const response = await api.get<ComplianceRequirement[]>('/compliance', { params })
  return response.data
}

export async function getComplianceSummary() {
  const response = await api.get<ComplianceSummary>('/compliance/summary')
  return response.data
}

export async function listInspections(status?: string) {
  const response = await api.get<Inspection[]>('/inspections', { params: status ? { status } : {} })
  return response.data
}

export async function createInspection(payload: { inspection_code: string; mine_id: number; zone_id: number | null; checklist_name: string; findings: string; remarks: string; evidence_path: string; checklist_items: Omit<ChecklistItem, 'id'>[] }) {
  const response = await api.post<Inspection>('/inspections', payload)
  return response.data
}

export async function updateInspection(id: number, payload: { status?: string; findings?: string; remarks?: string; evidence_path?: string }) {
  const response = await api.patch<Inspection>(`/inspections/${id}`, payload)
  return response.data
}

export async function listViolations(params: { status?: string; severity?: string } = {}) {
  const response = await api.get<Violation[]>('/violations', { params })
  return response.data
}

export async function getViolationSummary() {
  const response = await api.get<ViolationSummary>('/violations/summary')
  return response.data
}

export async function createViolation(payload: { violation_code: string; mine_id: number; zone_id: number | null; category: string; description: string; severity: string; due_date: string | null; evidence_path: string; assigned_officer: string }) {
  const response = await api.post<Violation>('/violations', payload)
  return response.data
}

export async function updateViolation(id: number, payload: { status?: string; severity?: string; assigned_officer?: string; evidence_path?: string }) {
  const response = await api.patch<Violation>(`/violations/${id}`, payload)
  return response.data
}

export async function listCAPA(status?: string) { const response = await api.get<CAPA[]>('/corrective-actions', { params: status ? { status } : {} }); return response.data }
export async function getCAPASummary() { const response = await api.get<CAPASummary>('/corrective-actions/summary'); return response.data }
export async function createCAPA(payload: { action_code: string; violation_id: number; description: string; responsible_person_id: number; contractor_id: number | null; priority: string; deadline: string; evidence_path: string }) { const response = await api.post<CAPA>('/corrective-actions', payload); return response.data }
export async function updateCAPA(id: number, payload: { status?: string; evidence_path?: string; verification?: string }) { const response = await api.patch<CAPA>(`/corrective-actions/${id}`, payload); return response.data }

export async function listContractors(params: { search?: string; status?: string } = {}) { const response = await api.get<Contractor[]>('/contractors', { params }); return response.data }
export async function getContractorSummary() { const response = await api.get<ContractorSummary>('/contractors/summary'); return response.data }
export async function createContractor(payload: Omit<Contractor, 'id' | 'workers'>) { const response = await api.post<Contractor>('/contractors', payload); return response.data }
export async function addContractorWorker(id: number, payload: Omit<ContractorWorker, 'id'>) { const response = await api.post<ContractorWorker>(`/contractors/${id}/workers`, payload); return response.data }
export async function listAlerts(params: { status?: string; severity?: string } = {}) { const response = await api.get<Alert[]>('/alerts', { params }); return response.data }
export async function getAlertSummary() { const response = await api.get<AlertSummary>('/alerts/summary'); return response.data }
export async function updateAlert(id: number, status: string) { const response = await api.patch<Alert>(`/alerts/${id}`, undefined, { params: { status } }); return response.data }
export async function listAudit(params: { action?: string; entity?: string; search?: string } = {}) { const response = await api.get<AuditLog[]>('/audit', { params }); return response.data }
export async function getAuditSummary() { const response = await api.get<AuditSummary>('/audit/summary'); return response.data }
export async function runPPEDetection(payload: { mine_id: number; zone_id: number | null; camera: string; case: string }) { const response = await api.post<PPEResult>('/ai/ppe/detect', payload); return response.data }
export async function listRiskEvents(params: { mine_id?: number; level?: string } = {}) { const response = await api.get<RiskEvent[]>('/risk', { params }); return response.data }
export async function calculateRisk(payload: { mine_id: number; zone_id: number | null; event_type: string; severity: number; likelihood: number; exposure: number; recurrence: number }) { const response = await api.post<RiskEvent>('/risk/calculate', payload); return response.data }
export async function detectAnomaly(payload: { mine_id: number; zone_id: number | null; metric: string; value: number }) { const response = await api.post<AnomalyResult>('/anomaly/detect', payload); return response.data }
export async function listDocuments() { const response = await api.get<DocumentRecord[]>('/documents'); return response.data }
export async function uploadDocument(file: File, documentType: string, mineId: number | null) { const form = new FormData(); form.append('file', file); form.append('document_type', documentType); if (mineId !== null) form.append('mine_id', String(mineId)); const response = await api.post<DocumentRecord>('/documents', form, { headers: { 'Content-Type': 'multipart/form-data' } }); return response.data }
export async function verifyDocument(id: number, status: string) { const response = await api.patch<DocumentRecord>(`/documents/${id}/verification`, { status }); return response.data }
export async function getGISMap() { const response = await api.get<GISMapResponse>('/gis/map'); return response.data }
export async function listIoTSensors() { const response = await api.get<IoTSensor[]>('/iot'); return response.data }
export async function simulateIoT(sensorId?: number) { const response = await api.post<IoTSimulation>('/iot/simulate', undefined, { params: sensorId ? { sensor_id: sensorId } : {} }); return response.data }
export async function updateIoTThreshold(id: number, threshold: number) { const response = await api.patch<IoTSensor>(`/iot/${id}/threshold`, { threshold }); return response.data }
export async function getReport(reportType: string, params: { mine_id?: number; date_from?: string; date_to?: string; severity?: string; status?: string; category?: string } = {}) { const response = await api.get<ReportResponse>(`/reports/${reportType}`, { params }); return response.data }
export async function downloadReportCsv(reportType: string, params: { mine_id?: number; date_from?: string; date_to?: string; severity?: string; status?: string; category?: string } = {}) { const response = await api.get<Blob>(`/reports/${reportType}/csv`, { params, responseType: 'blob' }); return response.data }
export async function getWorkflowSummary() { const response = await api.get<WorkflowSummary>('/workflow/summary'); return response.data }
