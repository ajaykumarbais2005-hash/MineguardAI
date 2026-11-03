import { useCallback, useEffect, useState } from 'react'
import { ClipboardList, Search } from 'lucide-react'
import { getAuditSummary, listAudit, type AuditLog, type AuditSummary } from '../services/api'

const zero: AuditSummary = { total: 0, today: 0, creates: 0, updates: 0, deletes: 0 }

export default function AuditTrailPage() {
  const [items, setItems] = useState<AuditLog[]>([])
  const [summary, setSummary] = useState(zero)
  const [action, setAction] = useState('')
  const [entity, setEntity] = useState('')
  const [search, setSearch] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setIsLoading(true)
    try {
      const [logs, totals] = await Promise.all([
        listAudit({ action: action || undefined, entity: entity || undefined, search: search || undefined }),
        getAuditSummary(),
      ])
      setItems(logs)
      setSummary(totals)
      setError('')
    } catch {
      setError('Audit trail is available to administrators and auditors only.')
    } finally {
      setIsLoading(false)
    }
  }, [action, entity, search])

  useEffect(() => {
    void load()
  }, [load])

  return (
    <div className="audit-management">
      <div className="module-heading">
        <div>
          <h2>Audit trail</h2>
          <p>Trace important changes across the MineGuard operational system.</p>
        </div>
        <span className="demo-chip">ACCESS CONTROLLED</span>
      </div>
      <div className="audit-summary">
        <div><ClipboardList size={18} /><span>Total events<strong>{summary.total}</strong></span></div>
        <div><span>Today<strong>{summary.today}</strong></span></div>
        <div><span>Creates<strong>{summary.creates}</strong></span></div>
        <div><span>Updates<strong>{summary.updates}</strong></span></div>
        <div><span>Deletes<strong>{summary.deletes}</strong></span></div>
      </div>
      <div className="audit-toolbar">
        <label className="search-field">
          <Search size={16} />
          <input
            aria-label="Search audit trail"
            placeholder="Search event descriptions..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </label>
        <select aria-label="Filter audit action" value={action} onChange={(event) => setAction(event.target.value)}>
          <option value="">All actions</option>
          <option value="CREATE">Create</option>
          <option value="UPDATE">Update</option>
          <option value="DELETE">Delete</option>
          <option value="LOGIN_SUCCESS">Successful login</option>
          <option value="LOGIN_FAILURE">Failed login</option>
          <option value="AUTH_FAILURE">Authentication failure</option>
          <option value="ACCESS_DENIED">Access denied</option>
          <option value="LOGOUT">Logout</option>
        </select>
        <select aria-label="Filter audit entity" value={entity} onChange={(event) => setEntity(event.target.value)}>
          <option value="">All entities</option>
          <option value="Mine">Mine</option>
          <option value="Violation">Violation</option>
          <option value="CorrectiveAction">CAPA</option>
          <option value="Alert">Alert</option>
          <option value="Authentication">Authentication</option>
          <option value="SYSTEM">System</option>
        </select>
      </div>
      {error && <p className="module-error" role="alert">{error}</p>}
      <div className="audit-table-wrap">
        <table className="audit-table">
          <thead>
            <tr><th>Event</th><th>Actor</th><th>Entity</th><th>Source</th><th>Timestamp</th></tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td className="table-state" colSpan={5}><span className="module-loading" role="status">Loading audit events…</span></td></tr>
            ) : items.length === 0 ? (
              <tr><td className="table-state" colSpan={5}>No audit events match the current filters.</td></tr>
            ) : items.map((item) => (
              <tr key={item.id}>
                <td>
                  <span className={`audit-action audit-${item.action.toLowerCase()}`}>{item.action}</span>
                  <strong>{item.description}</strong>
                </td>
                <td>{item.user_name ?? 'System'}<small>{item.user_email ?? 'Automated event'}</small></td>
                <td>{item.entity}<small>{item.entity_id ?? '—'}</small></td>
                <td>{item.ip_address ?? 'Not captured'}</td>
                <td>{new Date(item.created_at).toLocaleString('en-IN')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
