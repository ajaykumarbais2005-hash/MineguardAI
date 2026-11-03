import { useEffect, useState } from 'react'
import { Download, FileText, RefreshCw } from 'lucide-react'
import { downloadReportCsv, getReport, listMines, type Mine, type ReportResponse } from '../services/api'

const reportTypes = [{ value: 'compliance', label: 'Compliance Report' }, { value: 'inspection', label: 'Inspection Report' }, { value: 'violation', label: 'Violation Report' }, { value: 'capa', label: 'CAPA Report' }, { value: 'contractor', label: 'Contractor Report' }, { value: 'risk', label: 'Risk Report' }, { value: 'ai', label: 'AI Safety Report' }, { value: 'iot', label: 'IoT Report' }]

type Filters = { mine_id?: number; date_from?: string; date_to?: string; severity?: string; status?: string; category?: string }

export default function ReportsPage() {
  const [reportType, setReportType] = useState('compliance')
  const [filters, setFilters] = useState<Filters>({})
  const [mines, setMines] = useState<Mine[]>([])
  const [report, setReport] = useState<ReportResponse | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function load(nextType = reportType, nextFilters = filters) {
    setBusy(true)
    try {
      setReport(await getReport(nextType, nextFilters))
      setError('')
    } catch {
      setError('Report could not be generated.')
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    void listMines().then(setMines).catch(() => setError('Mines could not be loaded.'))
    void load()
  }, [])

  function updateFilter(name: keyof Filters, value: string) {
    setFilters((current) => ({ ...current, [name]: value || undefined }))
  }

  async function download() {
    try {
      const blob = await downloadReportCsv(reportType, filters)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `mineguard-${reportType}-report.csv`
      link.click()
      URL.revokeObjectURL(url)
    } catch {
      setError('CSV export could not be generated.')
    }
  }

  const columns = report?.rows[0] ? Object.keys(report.rows[0]) : []

  return <div className="reports-management">
    <div className="module-heading"><div><h2>Reports</h2><p>Generate filtered operational reports and export the current result as CSV.</p></div><span className="demo-chip">EXPORT READY</span></div>
    <section className="report-filter-panel"><div className="report-filter-heading"><FileText size={21} /><div><h3>Report builder</h3><p>Filters are applied to the live API result.</p></div></div><div className="report-filter-grid"><label>Report type<select value={reportType} onChange={(event) => { setReportType(event.target.value); void load(event.target.value, filters) }}>{reportTypes.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}</select></label><label>Mine<select value={filters.mine_id ?? ''} onChange={(event) => updateFilter('mine_id', event.target.value)}><option value="">All mines</option>{mines.map((mine) => <option key={mine.id} value={mine.id}>{mine.mine_name}</option>)}</select></label><label>From<input type="date" value={filters.date_from ?? ''} onChange={(event) => updateFilter('date_from', event.target.value)} /></label><label>To<input type="date" value={filters.date_to ?? ''} onChange={(event) => updateFilter('date_to', event.target.value)} /></label><label>Severity<input placeholder="HIGH" value={filters.severity ?? ''} onChange={(event) => updateFilter('severity', event.target.value)} /></label><label>Status<input placeholder="OPEN" value={filters.status ?? ''} onChange={(event) => updateFilter('status', event.target.value)} /></label><label>Category<input placeholder="PPE" value={filters.category ?? ''} onChange={(event) => updateFilter('category', event.target.value)} /></label></div><div className="report-actions"><button className="primary-action" type="button" disabled={busy} onClick={() => void load()}><RefreshCw size={16} />{busy ? 'Generating...' : 'Generate report'}</button><button type="button" disabled={!report || busy} onClick={() => void download()}><Download size={16} />Download CSV</button></div></section>
    {error && <p className="module-error" role="alert">{error}</p>}
    <section className="report-result-panel"><div className="list-heading"><div><p className="eyebrow">{report?.mode ?? 'LIVE API'}</p><h3>{reportTypes.find((type) => type.value === reportType)?.label}</h3></div><span>{report?.rows.length ?? 0} records</span></div>{!report || report.rows.length === 0 ? <p className="inspection-empty">No records match the selected filters.</p> : <div className="report-table-wrap"><table className="report-table"><thead><tr>{columns.map((column) => <th key={column}>{column.replaceAll('_', ' ')}</th>)}</tr></thead><tbody>{report.rows.map((row, index) => <tr key={index}>{columns.map((column) => <td key={column}>{String(row[column] ?? '—')}</td>)}</tr>)}</tbody></table></div>}</section>
  </div>
}
