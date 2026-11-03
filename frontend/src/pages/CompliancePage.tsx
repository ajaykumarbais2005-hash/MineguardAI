import { useEffect, useState } from 'react'
import { Search, ShieldAlert, ShieldCheck, TriangleAlert } from 'lucide-react'

import { getComplianceSummary, listCompliance, type ComplianceRequirement, type ComplianceSummary } from '../services/api'

const emptySummary: ComplianceSummary = { compliant: 0, partially_compliant: 0, non_compliant: 0, overdue: 0, critical: 0, total: 0 }

export default function CompliancePage() {
  const [requirements, setRequirements] = useState<ComplianceRequirement[]>([])
  const [summary, setSummary] = useState(emptySummary)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      setIsLoading(true)
      try {
        const [items, totals] = await Promise.all([listCompliance({ search, status: status || undefined }), getComplianceSummary()])
        setRequirements(items)
        setSummary(totals)
        setError('')
      } catch {
        setError('Unable to load compliance requirements. Confirm the backend is running.')
      } finally {
        setIsLoading(false)
      }
    }
    void load()
  }, [search, status])

  return <div className="compliance-management">
    <div className="module-heading"><div><h2>Compliance control</h2><p>Track statutory requirements and upcoming verification obligations.</p></div><span className="demo-chip">LIVE API</span></div>
    <div className="compliance-summary"><div><ShieldCheck size={19} /><span>Compliant<strong>{summary.compliant}</strong></span></div><div><TriangleAlert size={19} /><span>Partially compliant<strong>{summary.partially_compliant}</strong></span></div><div><ShieldAlert size={19} /><span>Non-compliant<strong>{summary.non_compliant}</strong></span></div><div><ShieldAlert size={19} /><span>Overdue<strong>{summary.overdue}</strong></span></div><div><ShieldAlert size={19} /><span>Critical<strong>{summary.critical}</strong></span></div></div>
    <div className="compliance-toolbar"><label className="search-field"><Search size={16} /><input aria-label="Search compliance requirements" placeholder="Search requirements, regulation, category..." value={search} onChange={(event) => setSearch(event.target.value)} /></label><select aria-label="Filter compliance status" value={status} onChange={(event) => setStatus(event.target.value)}><option value="">All statuses</option><option value="COMPLIANT">Compliant</option><option value="PARTIALLY_COMPLIANT">Partially compliant</option><option value="NON_COMPLIANT">Non-compliant</option><option value="OVERDUE">Overdue</option><option value="CRITICAL">Critical</option></select></div>
    {error && <p className="module-error" role="alert">{error}</p>}
    <div className="compliance-table-wrap"><table className="compliance-table"><thead><tr><th>Requirement</th><th>Category</th><th>Reference</th><th>Frequency</th><th>Next due</th><th>Status</th></tr></thead><tbody>{isLoading ? <tr><td className="table-state" colSpan={6}>Loading compliance register...</td></tr> : requirements.length === 0 ? <tr><td className="table-state" colSpan={6}>No requirements match the current filters.</td></tr> : requirements.map((item) => <tr key={item.id}><td><strong>{item.title}</strong><small>{item.requirement_code} / {item.mandatory ? 'Mandatory' : 'Advisory'}</small></td><td>{item.category}</td><td>{item.regulation_reference}</td><td>{item.frequency}</td><td>{item.next_due_date ? new Date(item.next_due_date).toLocaleDateString('en-IN') : 'Not scheduled'}</td><td><span className={`table-badge compliance-${item.status.toLowerCase()}`}>{item.status.replaceAll('_', ' ')}</span></td></tr>)}</tbody></table></div>
  </div>
}
