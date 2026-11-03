import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Edit3, Eye, Plus, Search, Trash2, X } from 'lucide-react'

import { createMine, deleteMine, getMine, listMines, updateMine, type Mine, type MineDetail } from '../services/api'


type MineForm = Omit<Mine, 'id' | 'manager_name' | 'created_at'>

const emptyMine: MineForm = {
  mine_name: '', mine_code: '', location: '', state: '', district: '', mine_type: 'OPEN_CAST', operator: '', production_capacity: null, current_production: null, status: 'ACTIVE', risk_level: 'MEDIUM', manager_id: null, latitude: null, longitude: null,
}

const fieldLabels: Array<[keyof MineForm, string]> = [['mine_name', 'Mine name'], ['mine_code', 'Mine code'], ['location', 'Location'], ['state', 'State'], ['district', 'District'], ['operator', 'Operator']]

export default function MinesPage() {
  const [mines, setMines] = useState<Mine[]>([])
  const [selectedMine, setSelectedMine] = useState<MineDetail | null>(null)
  const [form, setForm] = useState<MineForm>(emptyMine)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [riskFilter, setRiskFilter] = useState('')
  const [sortBy, setSortBy] = useState('mine_name')
  const [descending, setDescending] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const loadMines = useCallback(async () => {
    try {
      // oxlint-disable-next-line react(set-state-in-effect)
      setMines(await listMines({ search, status: statusFilter || undefined, risk_level: riskFilter || undefined, sort_by: sortBy, descending }))
      setError('')
    } catch {
      setError('Unable to load mines. Confirm the backend is running and your session is valid.')
    } finally {
      setIsLoading(false)
    }
  }, [descending, riskFilter, search, sortBy, statusFilter])

  useEffect(() => { void loadMines() }, [loadMines])

  function openCreate() {
    setEditingId(null)
    setForm(emptyMine)
    setIsFormOpen(true)
  }

  function openEdit(mine: Mine) {
    setEditingId(mine.id)
    setForm({ mine_name: mine.mine_name, mine_code: mine.mine_code, location: mine.location, state: mine.state, district: mine.district, mine_type: mine.mine_type, operator: mine.operator, production_capacity: mine.production_capacity, current_production: mine.current_production, status: mine.status, risk_level: mine.risk_level, manager_id: mine.manager_id, latitude: mine.latitude, longitude: mine.longitude })
    setIsFormOpen(true)
  }

  async function openDetails(id: number) {
    try {
      setSelectedMine(await getMine(id))
      setError('')
    } catch {
      setError('Unable to load mine details.')
    }
  }

  async function saveMine(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    try {
      if (editingId) await updateMine(editingId, form)
      else await createMine(form)
      setIsFormOpen(false)
      await loadMines()
    } catch {
      setError('Mine could not be saved. Check the code is unique and all fields are valid.')
    }
  }

  async function removeMine(mine: Mine) {
    if (!window.confirm(`Delete ${mine.mine_name}? Mines with related records cannot be deleted.`)) return
    try {
      await deleteMine(mine.id)
      await loadMines()
    } catch {
      setError('Mine could not be deleted. Related records may still exist.')
    }
  }

  function updateField(field: keyof MineForm, value: string) {
    const numericFields: Array<keyof MineForm> = ['production_capacity', 'current_production', 'manager_id', 'latitude', 'longitude']
    setForm((current) => ({ ...current, [field]: numericFields.includes(field) ? (value === '' ? null : Number(value)) : value }))
  }

  return <div className="mine-management">
    <div className="module-heading"><div><h2>Mine management</h2><p>Monitor site status, risk, production, and operating zones.</p></div><button className="primary-action" type="button" onClick={openCreate}><Plus size={17} />Add mine</button></div>
    <div className="mine-toolbar"><label className="search-field"><Search size={16} /><input aria-label="Search mines" placeholder="Search by mine, code, location..." value={search} onChange={(event) => setSearch(event.target.value)} /></label><select aria-label="Filter by status" value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="">All statuses</option><option value="ACTIVE">Active</option><option value="MAINTENANCE">Maintenance</option></select><select aria-label="Filter by risk" value={riskFilter} onChange={(event) => setRiskFilter(event.target.value)}><option value="">All risk levels</option><option value="LOW">Low risk</option><option value="MEDIUM">Medium risk</option><option value="HIGH">High risk</option><option value="CRITICAL">Critical risk</option></select><select aria-label="Sort mines" value={sortBy} onChange={(event) => setSortBy(event.target.value)}><option value="mine_name">Sort: Name</option><option value="risk_level">Sort: Risk</option><option value="status">Sort: Status</option><option value="created_at">Sort: Newest</option></select><button className="sort-button" type="button" onClick={() => setDescending((value) => !value)}>{descending ? 'Z-A / high' : 'A-Z / low'}</button></div>
    {error && <p className="module-error" role="alert">{error}</p>}
    <div className="mine-summary"><span><strong>{mines.length.toString().padStart(2, '0')}</strong> sites shown</span><span className="demo-chip">LIVE API</span></div>
    <div className="mine-table-wrap"><table className="mine-table"><thead><tr><th>Mine</th><th>Location</th><th>Operator</th><th>Production</th><th>Status</th><th>Risk</th><th aria-label="Actions" /></tr></thead><tbody>{isLoading ? <tr><td className="table-state" colSpan={7}><span className="module-loading" role="status">Loading mine register…</span></td></tr> : error && mines.length === 0 ? <tr><td className="table-state" colSpan={7}>Mine register unavailable.</td></tr> : mines.length === 0 ? <tr><td className="table-state" colSpan={7}>No mines match the current filters.</td></tr> : mines.map((mine) => <tr key={mine.id}><td><strong>{mine.mine_name}</strong><small>{mine.mine_code} / {mine.mine_type.replace('_', ' ')}</small></td><td>{mine.location}<small>{mine.state}</small></td><td>{mine.operator}</td><td>{mine.current_production ?? 0} / {mine.production_capacity ?? 0} MT</td><td><span className={`table-badge status-${mine.status.toLowerCase()}`}>{mine.status.replace('_', ' ')}</span></td><td><span className={`table-badge risk-${mine.risk_level.toLowerCase()}`}>{mine.risk_level}</span></td><td><div className="table-actions"><button type="button" aria-label={`View ${mine.mine_name}`} onClick={() => void openDetails(mine.id)}><Eye size={16} /></button><button type="button" aria-label={`Edit ${mine.mine_name}`} onClick={() => openEdit(mine)}><Edit3 size={16} /></button><button type="button" aria-label={`Delete ${mine.mine_name}`} onClick={() => void removeMine(mine)}><Trash2 size={16} /></button></div></td></tr>)}</tbody></table></div>
    {selectedMine && <div className="detail-drawer"><div className="drawer-heading"><div><p className="eyebrow accent">Mine profile</p><h3>{selectedMine.mine_name}</h3><span>{selectedMine.mine_code} / {selectedMine.location}</span></div><button type="button" aria-label="Close mine details" onClick={() => setSelectedMine(null)}><X size={18} /></button></div><div className="detail-stats"><div><strong>{selectedMine.statistics.zone_count}</strong><span>Zones</span></div><div><strong>{selectedMine.statistics.inspection_count}</strong><span>Inspections</span></div><div><strong>{selectedMine.statistics.open_violation_count}</strong><span>Open violations</span></div><div><strong>{selectedMine.statistics.active_sensor_count}</strong><span>Live sensors</span></div></div><h4>Operating zones</h4><div className="zone-list">{selectedMine.zones.map((zone) => <div key={zone.id}><span>{zone.name}</span><small>{zone.zone_type} / {zone.status}</small></div>)}</div><div className="detail-grid"><span>Risk level<strong>{selectedMine.risk_level}</strong></span><span>Mine type<strong>{selectedMine.mine_type.replace('_', ' ')}</strong></span><span>Coordinates<strong>{selectedMine.latitude ?? '—'}, {selectedMine.longitude ?? '—'}</strong></span><span>Manager<strong>{selectedMine.manager_name ?? 'Unassigned'}</strong></span></div></div>}
  {isFormOpen && <div className="modal-backdrop"><section className="mine-modal"><div className="drawer-heading"><div><p className="eyebrow accent">Asset register</p><h3>{editingId ? 'Edit mine' : 'Add mine'}</h3></div><button type="button" aria-label="Close mine form" onClick={() => setIsFormOpen(false)}><X size={18} /></button></div><form className="mine-form" onSubmit={saveMine}>{fieldLabels.map(([field, label]) => <label key={field}>{label}<input required value={form[field] as string} onChange={(event) => updateField(field, event.target.value)} /></label>)}<label>Mine type<select value={form.mine_type} onChange={(event) => updateField('mine_type', event.target.value)}><option value="OPEN_CAST">Open cast</option><option value="UNDERGROUND">Underground</option></select></label><div className="form-columns"><label>Status<select value={form.status} onChange={(event) => updateField('status', event.target.value)}><option value="ACTIVE">Active</option><option value="MAINTENANCE">Maintenance</option><option value="CLOSED">Closed</option></select></label><label>Risk level<select value={form.risk_level} onChange={(event) => updateField('risk_level', event.target.value)}><option value="LOW">Low</option><option value="MEDIUM">Medium</option><option value="HIGH">High</option><option value="CRITICAL">Critical</option></select></label></div><div className="form-columns"><label>Capacity MT<input type="number" min="0" step="0.1" value={form.production_capacity ?? ''} onChange={(event) => updateField('production_capacity', event.target.value)} /></label><label>Current MT<input type="number" min="0" step="0.1" value={form.current_production ?? ''} onChange={(event) => updateField('current_production', event.target.value)} /></label></div><div className="form-columns"><label>Latitude<input type="number" min="-90" max="90" step="any" value={form.latitude ?? ''} onChange={(event) => updateField('latitude', event.target.value)} /></label><label>Longitude<input type="number" min="-180" max="180" step="any" value={form.longitude ?? ''} onChange={(event) => updateField('longitude', event.target.value)} /></label></div><div className="modal-actions"><button className="secondary-action" type="button" onClick={() => setIsFormOpen(false)}>Cancel</button><button className="primary-action" type="submit">{editingId ? 'Save changes' : 'Create mine'}</button></div></form></section></div>}
+  </div>
}
