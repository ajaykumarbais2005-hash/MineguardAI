import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { ClipboardCheck, Plus, X } from 'lucide-react'

import { createInspection, listInspections, updateInspection, type Inspection } from '../services/api'

const checklist = [
  { item_code: 'PPE-01', question: 'Are all personnel wearing approved helmets?' },
  { item_code: 'PPE-02', question: 'Are high-visibility vests and safety boots in use?' },
  { item_code: 'OPS-01', question: 'Is the work area free from immediate hazards?' },
]

export default function InspectionsPage() {
  const [inspections, setInspections] = useState<Inspection[]>([])
  const [status, setStatus] = useState('')
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ inspection_code: 'INS-NEW-0001', mine_id: 1, zone_id: 1, checklist_name: 'Daily Safety Round', findings: '', remarks: '', evidence_path: '' })

  const load = useCallback(async () => {
    try { setInspections(await listInspections(status || undefined)); setError('') } catch { setError('Unable to load inspection register.') } finally { setIsLoading(false) }
  }, [status])
  useEffect(() => { void load() }, [load])

  async function submitInspection(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    try {
      await createInspection({ ...form, checklist_items: checklist.map((item) => ({ ...item, response: null, remarks: null })) })
      setIsFormOpen(false)
      await load()
    } catch { setError('Inspection could not be created. Verify the mine and zone selection.') }
  }

  async function submitForReview(id: number) {
    try { await updateInspection(id, { status: 'SUBMITTED' }); await load() } catch { setError('Inspection status could not be updated.') }
  }

  return <div className="inspection-management">
    <div className="module-heading"><div><p className="eyebrow accent">Field assurance / Phase 09</p><h2>Inspections</h2><p>Plan safety rounds, record findings, and submit evidence for review.</p></div><button className="primary-action" type="button" onClick={() => setIsFormOpen(true)}><Plus size={17} />New inspection</button></div>
    <div className="inspection-toolbar"><span className="inspection-count"><ClipboardCheck size={17} />{inspections.length} inspection records</span><select aria-label="Filter inspection status" value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option><option value="DRAFT">Draft</option><option value="IN_PROGRESS">In progress</option><option value="SUBMITTED">Submitted</option><option value="REVIEWED">Reviewed</option><option value="CLOSED">Closed</option></select></div>
    {error && <p className="module-error" role="alert">{error}</p>}
    <div className="inspection-list">{isLoading ? <div className="inspection-empty">Loading inspection register...</div> : inspections.length === 0 ? <div className="inspection-empty">No inspections match this status.</div> : inspections.map((item) => <article className="inspection-card" key={item.id}><div className="inspection-card-heading"><div><span className="inspection-code">{item.inspection_code}</span><h3>{item.checklist_name}</h3><p>{item.mine_name} / {item.zone_name ?? 'All zones'}</p></div><span className={`table-badge inspection-${item.status.toLowerCase()}`}>{item.status.replaceAll('_', ' ')}</span></div><div className="inspection-meta"><span>Started<strong>{new Date(item.started_at).toLocaleDateString('en-IN')}</strong></span><span>Checklist<strong>{item.checklist_items.length} items</strong></span><span>Findings<strong>{item.findings || 'No findings recorded'}</strong></span></div>{item.status !== 'SUBMITTED' && item.status !== 'CLOSED' && <button className="secondary-action" type="button" onClick={() => void submitForReview(item.id)}>Submit for review</button>}</article>)}</div>
    {isFormOpen && <div className="modal-backdrop"><section className="mine-modal inspection-modal"><div className="drawer-heading"><div><p className="eyebrow accent">Field record</p><h3>New inspection</h3></div><button type="button" aria-label="Close inspection form" onClick={() => setIsFormOpen(false)}><X size={18} /></button></div><form className="inspection-form" onSubmit={submitInspection}><label>Inspection code<input required value={form.inspection_code} onChange={(event) => setForm({ ...form, inspection_code: event.target.value })} /></label><label>Checklist<select value={form.checklist_name} onChange={(event) => setForm({ ...form, checklist_name: event.target.value })}><option>Daily Safety Round</option><option>Transport Safety</option><option>Underground Ventilation</option></select></label><div className="form-columns"><label>Mine ID<input type="number" min="1" value={form.mine_id} onChange={(event) => setForm({ ...form, mine_id: Number(event.target.value) })} /></label><label>Zone ID<input type="number" min="1" value={form.zone_id} onChange={(event) => setForm({ ...form, zone_id: Number(event.target.value) })} /></label></div><div className="checklist-editor"><h4>Checklist items</h4>{checklist.map((item) => <div key={item.item_code}><span>{item.item_code}</span><p>{item.question}</p><select aria-label={`${item.item_code} response`}><option value="">Pending</option><option value="YES">Yes</option><option value="NO">No</option><option value="NA">N/A</option></select></div>)}</div><label>Findings<textarea value={form.findings} onChange={(event) => setForm({ ...form, findings: event.target.value })} placeholder="Record observations and non-conformities" /></label><label>Remarks<textarea value={form.remarks} onChange={(event) => setForm({ ...form, remarks: event.target.value })} placeholder="Add handover or follow-up notes" /></label><label>Evidence reference<input value={form.evidence_path} onChange={(event) => setForm({ ...form, evidence_path: event.target.value })} placeholder="data/uploads/evidence.jpg" /></label><div className="modal-actions"><button className="secondary-action" type="button" onClick={() => setIsFormOpen(false)}>Cancel</button><button className="primary-action" type="submit">Create inspection</button></div></form></section></div>}
  </div>
}
