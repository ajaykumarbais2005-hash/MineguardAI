import { useEffect, useState } from 'react'
import { Calculator, RefreshCw, ShieldAlert } from 'lucide-react'
import { calculateRisk, detectAnomaly, getMine, listMines, listRiskEvents, type AnomalyResult, type Mine, type MineZone, type RiskEvent } from '../services/api'

const initialFactors = { severity: 3, likelihood: 3, exposure: 3, recurrence: 3 }

export default function RiskAnalyticsPage() {
  const [mines, setMines] = useState<Mine[]>([])
  const [zones, setZones] = useState<MineZone[]>([])
  const [mineId, setMineId] = useState<number | null>(null)
  const [zoneId, setZoneId] = useState<number | null>(null)
  const [eventType, setEventType] = useState('GENERAL_SAFETY')
  const [factors, setFactors] = useState(initialFactors)
  const [events, setEvents] = useState<RiskEvent[]>([])
  const [result, setResult] = useState<RiskEvent | null>(null)
  const [anomalyMetric, setAnomalyMetric] = useState('gas_level')
  const [anomalyValue, setAnomalyValue] = useState(40)
  const [anomalyResult, setAnomalyResult] = useState<AnomalyResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadMines() {
      try {
        const availableMines = await listMines({ status: 'ACTIVE' })
        setMines(availableMines)
        setMineId(availableMines[0]?.id ?? null)
      } catch {
        setError('Mines could not be loaded.')
      } finally {
        setLoading(false)
      }
    }
    void loadMines()
  }, [])

  useEffect(() => {
    if (mineId === null) {
      setZones([])
      setZoneId(null)
      return
    }
    async function loadMine() {
      try {
        const mine = await getMine(mineId as number)
        setZones(mine.zones)
        setZoneId(mine.zones[0]?.id ?? null)
      } catch {
        setError('Zones could not be loaded.')
      }
    }
    void loadMine()
  }, [mineId])

  useEffect(() => {
    async function loadEvents() {
      try {
        setEvents(await listRiskEvents(mineId === null ? {} : { mine_id: mineId }))
      } catch {
        setError('Risk history could not be loaded.')
      }
    }
    void loadEvents()
  }, [mineId, result])

  function updateFactor(name: keyof typeof factors, value: string) {
    setFactors((current) => ({ ...current, [name]: Number(value) }))
  }

  async function submit() {
    if (mineId === null) {
      setError('Select a mine before calculating risk.')
      return
    }
    setRunning(true)
    setError('')
    try {
      setResult(await calculateRisk({ mine_id: mineId, zone_id: zoneId, event_type: eventType, ...factors }))
    } catch {
      setError('Risk calculation failed. Check the selected mine and factor values.')
    } finally {
      setRunning(false)
    }
  }

  async function submitAnomaly() {
    if (mineId === null) {
      setError('Select a mine before checking for anomalies.')
      return
    }
    setRunning(true)
    setError('')
    try {
      setAnomalyResult(await detectAnomaly({ mine_id: mineId, zone_id: zoneId, metric: anomalyMetric, value: anomalyValue }))
    } catch {
      setError('Anomaly detection failed. Check the selected mine and reading.')
    } finally {
      setRunning(false)
    }
  }

  return <div className="risk-management">
    <div className="module-heading"><div><p className="eyebrow accent">Decision support / Phase 16</p><h2>Risk Analytics</h2><p>Calculate and record transparent safety risk from four operational factors.</p></div><span className="demo-chip">LIVE API</span></div>
    <section className="risk-calculator-panel">
      <div className="risk-panel-heading"><div><Calculator size={21} /><div><h3>Risk calculation</h3><p>Risk Score = Severity x Likelihood x Exposure x Recurrence, normalized to 0-100.</p></div></div><ShieldAlert size={22} /></div>
      <div className="risk-form-grid">
        <label>Mine<select aria-label="Risk mine" disabled={loading} value={mineId ?? ''} onChange={(event) => setMineId(event.target.value ? Number(event.target.value) : null)}><option value="">Select a mine</option>{mines.map((mine) => <option key={mine.id} value={mine.id}>{mine.mine_name}</option>)}</select></label>
        <label>Zone<select aria-label="Risk zone" value={zoneId ?? ''} disabled={mineId === null} onChange={(event) => setZoneId(event.target.value ? Number(event.target.value) : null)}><option value="">All mine zones</option>{zones.map((zone) => <option key={zone.id} value={zone.id}>{zone.name}</option>)}</select></label>
        <label>Event type<input value={eventType} onChange={(event) => setEventType(event.target.value)} minLength={2} /></label>
        {(Object.keys(factors) as Array<keyof typeof factors>).map((factor) => <label key={factor}>{factor.charAt(0).toUpperCase() + factor.slice(1)}<input type="number" min="1" max="5" step="1" value={factors[factor]} onChange={(event) => updateFactor(factor, event.target.value)} /></label>)}
      </div>
      <button className="primary-action" type="button" disabled={running || mineId === null} onClick={() => void submit()}><Calculator size={16} />{running ? 'Calculating...' : 'Calculate risk'}</button>
    </section>
    {error && <p className="module-error" role="alert">{error}</p>}
    {result && <section className="risk-result-panel"><div><p className="eyebrow">Latest calculation / {result.event_type}</p><div className="risk-score"><strong>{result.score}</strong><span>/ 100</span><b className={`table-badge risk-${result.level.toLowerCase()}`}>{result.level}</b></div><p>{result.reason}</p><p><strong>Recommended action:</strong> {result.recommended_action}</p></div><div className="risk-factor-list">{(['severity', 'likelihood', 'exposure', 'recurrence'] as const).map((factor) => <span key={factor}>{factor}<strong>{result[factor]}</strong></span>)}</div></section>}
    <section className="risk-calculator-panel"><div className="risk-panel-heading"><div><ShieldAlert size={21} /><div><h3>Anomaly detection</h3><p>DEMO_SIMULATION checks operational signals against configured thresholds.</p></div></div></div><div className="risk-form-grid"><label>Metric<select aria-label="Anomaly metric" value={anomalyMetric} onChange={(event) => setAnomalyMetric(event.target.value)}><option value="gas_level">Gas level</option><option value="temperature">Temperature</option><option value="dust">Dust</option><option value="vehicle_speed">Vehicle speed</option><option value="production">Production</option><option value="inspection_frequency">Inspection frequency</option><option value="violation_frequency">Violation frequency</option><option value="contractor_performance">Contractor performance</option></select></label><label>Reading<input aria-label="Anomaly reading" type="number" value={anomalyValue} onChange={(event) => setAnomalyValue(Number(event.target.value))} /></label></div><button className="primary-action" type="button" disabled={running || mineId === null} onClick={() => void submitAnomaly()}><ShieldAlert size={16} />{running ? 'Checking...' : 'Check for anomaly'}</button>{anomalyResult && <div className="risk-result-panel"><div><p className="eyebrow">{anomalyResult.mode}</p><div className="risk-score"><strong>{anomalyResult.is_anomaly ? 'Anomaly' : 'Normal'}</strong>{anomalyResult.risk_level && <b className={`table-badge risk-${anomalyResult.risk_level.toLowerCase()}`}>{anomalyResult.risk_level}</b>}</div><p>{anomalyResult.reason}</p>{anomalyResult.risk_score !== null && <p><strong>Generated risk score:</strong> {anomalyResult.risk_score}</p>}</div></div>}</section>
    <section className="risk-history-panel"><div className="list-heading"><div><p className="eyebrow">Recorded decisions</p><h3>Risk event history</h3></div><button type="button" aria-label="Refresh risk history" onClick={() => setResult((current) => current ? { ...current } : null)}><RefreshCw size={17} /></button></div>{events.length === 0 ? <p className="inspection-empty">No risk events recorded for the selected scope.</p> : <div className="risk-history-list">{events.map((event) => <article key={event.id}><div><span className={`table-badge risk-${event.level.toLowerCase()}`}>{event.level}</span><strong>{event.event_type}</strong><small>{event.mine_name} / {event.zone_name ?? 'All zones'}</small></div><b>{event.score}</b></article>)}</div>}</section>
  </div>
}
