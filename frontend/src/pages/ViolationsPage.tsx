import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { AlertTriangle, Plus, X } from 'lucide-react'

import { createViolation, getViolationSummary, listViolations, updateViolation, type Violation, type ViolationSummary } from '../services/api'

const zeroSummary: ViolationSummary = { open: 0, assigned: 0, in_progress: 0, resolved: 0, verified: 0, closed: 0, critical: 0, total: 0 }

export default function ViolationsPage() {
  const [violations, setViolations] = useState<Violation[]>([])
  const [summary, setSummary] = useState(zeroSummary)
  const [status, setStatus] = useState('')
  const [severity, setSeverity] = useState('')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ violation_code: 'VIO-NEW-0001', mine_id: 1, zone_id: 1, category: 'PPE', description: '', severity: 'HIGH', due_date: '', evidence_path: '', assigned_officer: '' })

  const load = useCallback(async () => {
    setIsLoading(true)
    try { const [items, totals] = await Promise.all([listViolations({ status: status || undefined, severity: severity || undefined }), getViolationSummary()]); setViolations(items); setSummary(totals); setError('') } catch { setError('Unable to load violation register.') } finally { setIsLoading(false) }
  }, [severity, status])
  useEffect(() => { void load() }, [load])

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    try { await createViolation({ ...form, due_date: form.due_date || null }); setIsFormOpen(false); await load() } catch { setError('Violation could not be created. Verify the mine and zone references.') }
  }

  async function changeStatus(id: number, nextStatus: string) {
    try { await updateViolation(id, { status: nextStatus }); await load() } catch { setError('Violation status could not be updated.') }
  }

  return <div className="violation-management">
    <div className="module-heading"><div><p className="eyebrow accent">Incident control / Phase 10</p><h2>Violations</h2><p>Prioritize findings, assign ownership, and track resolution to closure.</p></div><button className="primary-action" type="button" onClick={() => setIsFormOpen(true)}><Plus size={17} />Record violation</button></div>
    <div className="violation-summary"><div><span>Open</span><strong>{summary.open}</strong></div><div><span>Assigned</span><strong>{summary.assigned}</strong></div><div><span>In progress</span><strong>{summary.in_progress}</strong></div><div><span>Critical</span><strong>{summary.critical}</strong></div><div><span>Total findings</span><strong>{summary.total}</strong></div></div>
    <div className="violation-toolbar"><span className="inspection-count"><AlertTriangle size={17} />Live violation register</span><select aria-label="Filter violation status" value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option><option value="OPEN">Open</option><option value="ASSIGNED">Assigned</option><option value="IN_PROGRESS">In progress</option><option value="RESOLVED">Resolved</option><option value="VERIFIED">Verified</option><option value="CLOSED">Closed</option></select><select aria-label="Filter violation severity" value={severity} onChange={(event) => setSeverity(event.target.value)}><option value="">All severity</option><option value="LOW">Low</option><option value="MEDIUM">Medium</option><option value="HIGH">High</option><option value="CRITICAL">Critical</option></select></div>
    {error && <p className="module-error" role="alert">{error}</p>}
    <div className="violation-list">{isLoading ? <div className="inspection-empty"><span className="module-loading" role="status">Loading violations…</span></div> : violations.length === 0 ? <div className="inspection-empty">No violations match the selected filters.</div> : violations.map((item) => <article className="violation-card" key={item.id}><div className="violation-card-heading"><div><span className="inspection-code">{item.violation_code}</span><h3>{item.description}</h3><p>{item.mine_name} / {item.zone_name ?? 'All zones'} / {item.category}</p></div><span className={`table-badge violation-${item.severity.toLowerCase()}`}>{item.severity}</span></div><div className="violation-meta"><span>Status<strong>{item.status.replaceAll('_', ' ')}</strong></span><span>Detected<strong>{new Date(item.detected_at).toLocaleDateString('en-IN')}</strong></span><span>Owner<strong>{item.assigned_officer || 'Unassigned'}</strong></span><span>Due<strong>{item.due_date ? new Date(item.due_date).toLocaleDateString('en-IN') : 'Not set'}</strong></span></div>{item.status !== 'CLOSED' && <select className="status-select" aria-label={`Update ${item.violation_code} status`} value={item.status} onChange={(event) => void changeStatus(item.id, event.target.value)}><option value="OPEN">Open</option><option value="ASSIGNED">Assigned</option><option value="IN_PROGRESS">In progress</option><option value="RESOLVED">Resolved</option><option value="VERIFIED">Verified</option><option value="CLOSED">Closed</option></select>}</article>)}</div>
    {isFormOpen && <div className="modal-backdrop"><section className="mine-modal"><div className="drawer-heading"><div><p className="eyebrow accent">Incident record</p><h3>Record violation</h3></div><button type="button" aria-label="Close violation form" onClick={() => setIsFormOpen(false)}><X size={18} /></button></div><form className="inspection-form" onSubmit={save}><div className="form-columns"><label>Violation code<input required value={form.violation_code} onChange={(event) => setForm({ ...form, violation_code: event.target.value })} /></label><label>Category<input required value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })} /></label></div><div className="form-columns"><label>Mine ID<input type="number" min="1" value={form.mine_id} onChange={(event) => setForm({ ...form, mine_id: Number(event.target.value) })} /></label><label>Zone ID<input type="number" min="1" value={form.zone_id} onChange={(event) => setForm({ ...form, zone_id: Number(event.target.value) })} /></label></div><label>Description<textarea required value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} placeholder="Describe the non-conformity" /></label><label>Severity<select value={form.severity} onChange={(event) => setForm({ ...form, severity: event.target.value })}><option>LOW</option><option>MEDIUM</option><option>HIGH</option><option>CRITICAL</option></select></label><div className="form-columns"><label>Due date<input type="date" value={form.due_date} onChange={(event) => setForm({ ...form, due_date: event.target.value })} /></label><label>Assigned officer<input value={form.assigned_officer} onChange={(event) => setForm({ ...form, assigned_officer: event.target.value })} /></label></div><label>Evidence reference<input value={form.evidence_path} onChange={(event) => setForm({ ...form, evidence_path: event.target.value })} placeholder="data/uploads/evidence.jpg" /></label><div className="modal-actions"><button className="secondary-action" type="button" onClick={() => setIsFormOpen(false)}>Cancel</button><button className="primary-action" type="submit">Create violation</button></div></form></section></div>}
  </div>
}
