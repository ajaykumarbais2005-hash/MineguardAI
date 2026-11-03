import { useEffect, useState } from 'react'
import { Camera, CheckCircle2, CircleAlert, Play, ShieldAlert } from 'lucide-react'
import { getMine, listMines, runPPEDetection, type Mine, type MineZone, type PPEResult } from '../services/api'

export default function AIMonitoringPageSelectable() {
  const [mines, setMines] = useState<Mine[]>([])
  const [mineId, setMineId] = useState<number | null>(null)
  const [zones, setZones] = useState<MineZone[]>([])
  const [zoneId, setZoneId] = useState<number | null>(null)
  const [scenario, setScenario] = useState('no_helmet')
  const [result, setResult] = useState<PPEResult | null>(null)
  const [running, setRunning] = useState(false)
  const [loadingMines, setLoadingMines] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadMines() {
      try {
        const availableMines = await listMines({ status: 'ACTIVE' })
        setMines(availableMines)
        setMineId(availableMines[0]?.id ?? null)
      } catch {
        setError('Mines could not be loaded. Confirm the backend is available.')
      } finally {
        setLoadingMines(false)
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
    const selectedMineId = mineId
    async function loadZones() {
      try {
        const mine = await getMine(selectedMineId)
        setZones(mine.zones)
        setZoneId(mine.zones[0]?.id ?? null)
      } catch {
        setZones([])
        setZoneId(null)
        setError('Zones could not be loaded for the selected mine.')
      }
    }
    void loadZones()
  }, [mineId])

  const selectedMine = mines.find((mine) => mine.id === mineId)

  async function run() {
    if (mineId === null) {
      setError('Select a mine before running the inspection.')
      return
    }
    setRunning(true)
    setError('')
    try {
      setResult(await runPPEDetection({ mine_id: mineId, zone_id: zoneId, camera: 'CAM-HAUL-01', case: scenario }))
    } catch {
      setError('AI inspection could not run. Confirm the backend is available.')
    } finally {
      setRunning(false)
    }
  }

  return <div className="ai-management">
    <div className="module-heading"><div><h2>AI Monitoring</h2><p>Run a transparent PPE inspection using the configured simulation boundary.</p></div><span className="demo-chip">AI DEMO MODE</span></div>
    <div className="ai-control-panel">
      <div className="ai-camera"><Camera size={28} /><div><strong>{selectedMine?.mine_name ?? 'No mine selected'}</strong><span>{zones.find((zone) => zone.id === zoneId)?.name ?? 'Select an operating zone'}</span></div><span className="live-chip"><span className="status-dot" />Ready</span></div>
      <div className="ai-controls">
        <label>Mine<select aria-label="Mine" value={mineId ?? ''} disabled={loadingMines} onChange={(event) => setMineId(event.target.value ? Number(event.target.value) : null)}><option value="">Select a mine</option>{mines.map((mine) => <option key={mine.id} value={mine.id}>{mine.mine_name}</option>)}</select></label>
        <label>Zone<select aria-label="Zone" value={zoneId ?? ''} disabled={mineId === null} onChange={(event) => setZoneId(event.target.value ? Number(event.target.value) : null)}><option value="">All mine zones</option>{zones.map((zone) => <option key={zone.id} value={zone.id}>{zone.name}</option>)}</select></label>
        <label>Simulation scenario<select value={scenario} onChange={(event) => setScenario(event.target.value)}><option value="no_helmet">Person without helmet</option><option value="no_helmet_no_vest">Person without helmet and vest</option><option value="compliant">Compliant PPE</option></select></label>
        <button className="primary-action" type="button" disabled={running || mineId === null} onClick={() => void run()}><Play size={16} />{running ? 'Analyzing...' : 'Run PPE inspection'}</button>
      </div>
    </div>
    {error && <p className="module-error" role="alert">{error}</p>}
    {result ? <section className="ai-result"><div className="ai-result-heading"><div><p className="eyebrow">Event #{result.event_id} / {result.mode}</p><h3>{result.event_type.replaceAll('_', ' ')}</h3><p>{result.disclaimer}</p></div><span className={`table-badge violation-${result.severity.toLowerCase()}`}>{result.severity}</span></div><div className="ai-result-meta"><span>Model<strong>{result.mode}</strong></span><span>Confidence<strong>{Math.round(result.confidence * 100)}%</strong></span><span>Camera<strong>{result.camera}</strong></span><span>Captured<strong>{new Date(result.created_at).toLocaleTimeString('en-IN')}</strong></span></div><div className="detection-grid">{result.detections.map((detection) => <div className={detection.present ? 'detection-present' : 'detection-missing'} key={detection.label}>{detection.present ? <CheckCircle2 size={18} /> : <ShieldAlert size={18} />}<span>{detection.label.replace('_', ' ')}</span><strong>{detection.present ? `${Math.round(detection.confidence * 100)}%` : 'Not detected'}</strong></div>)}</div>{result.workflow && <div className="workflow-chain"><p className="eyebrow">End-to-end workflow</p><span>Risk {result.workflow.risk_event_id ? 'created' : 'not created'}</span><span>Violation {result.workflow.violation_id ? 'created' : 'not created'}</span><span>Alert {result.workflow.alert_id ? 'created' : 'not created'}</span><span>CAPA {result.workflow.capa_id ? 'created' : 'not created'}</span><span>Contractor {result.workflow.contractor_id ? 'assigned' : 'not assigned'}</span></div>}</section> : <div className="ai-empty"><CircleAlert size={23} /><strong>No inspection result yet</strong><span>Select a mine, zone, and demo scenario to run the PPE inspection.</span></div>}
    <p className="dashboard-disclaimer"><span className="status-dot" />This result is simulated. No trained YOLO model or production accuracy is being claimed.</p>
  </div>
}
