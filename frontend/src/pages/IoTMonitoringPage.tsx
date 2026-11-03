import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, Gauge, RefreshCw, Save } from 'lucide-react'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { listIoTSensors, simulateIoT, updateIoTThreshold, type IoTSensor } from '../services/api'

const sensorColors: Record<string, string> = { Gas: '#b84f45', Temperature: '#e17d45', Dust: '#e4b44c', Humidity: '#3c78a8', 'Vehicle Speed': '#8e4d87', Vibration: '#4eac70' }

export default function IoTMonitoringPage() {
  const [sensors, setSensors] = useState<IoTSensor[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [thresholds, setThresholds] = useState<Record<number, string>>({})
  const [alertsCreated, setAlertsCreated] = useState(0)
  const [busy, setBusy] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    try {
      const items = await listIoTSensors()
      setSensors(items)
      setSelectedId((current) => current ?? items[0]?.id ?? null)
      setThresholds(Object.fromEntries(items.map((sensor) => [sensor.id, String(sensor.threshold)])))
      setError('')
    } catch {
      setError('Sensor data could not be loaded.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => { void load() }, [])

  async function simulate() {
    setBusy(true)
    setError('')
    try {
      const result = await simulateIoT()
      setSensors(result.sensors)
      setAlertsCreated(result.alerts_created)
    } catch {
      setError('Sensor simulation could not run.')
    } finally {
      setBusy(false)
    }
  }

  async function saveThreshold(sensor: IoTSensor) {
    setBusy(true)
    try {
      const updated = await updateIoTThreshold(sensor.id, Number(thresholds[sensor.id]))
      setSensors((current) => current.map((item) => item.id === updated.id ? { ...item, threshold: updated.threshold } : item))
    } catch {
      setError('Threshold could not be updated.')
    } finally {
      setBusy(false)
    }
  }

  const selected = sensors.find((sensor) => sensor.id === selectedId) ?? sensors[0]
  const chartData = selected?.readings.slice().reverse().map((reading) => ({ time: new Date(reading.recorded_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }), value: reading.value, threshold: selected.threshold })) ?? []

  return <div className="iot-management">
    <div className="module-heading"><div><h2>IoT Monitoring</h2><p>Monitor simulated mine telemetry, thresholds, and sensor alerts.</p></div><span className="demo-chip">SIMULATED SENSOR DATA</span></div>
    <div className="iot-toolbar"><span><Activity size={17} />{sensors.length} sensors online</span><span className="iot-alert-count"><AlertTriangle size={16} />{alertsCreated} alerts from last simulation</span><button className="primary-action" type="button" disabled={busy} onClick={() => void simulate()}><RefreshCw size={16} />{busy ? 'Simulating...' : 'Generate readings'}</button></div>
    {error && <p className="module-error" role="alert">{error}</p>}
    {isLoading ? <p className="inspection-empty"><span className="module-loading" role="status">Loading sensor readings…</span></p> : sensors.length === 0 ? <p className="inspection-empty">No sensors are configured for monitoring.</p> : <div className="iot-sensor-grid">{sensors.map((sensor) => <button type="button" className={selected?.id === sensor.id ? 'iot-sensor-card selected' : 'iot-sensor-card'} key={sensor.id} onClick={() => setSelectedId(sensor.id)}><span className="iot-sensor-icon" style={{ color: sensorColors[sensor.sensor_type] ?? '#31544a' }}><Gauge size={21} /></span><span><strong>{sensor.sensor_type}</strong><small>{sensor.sensor_code} / {sensor.mine_name}</small></span><b className={sensor.status === 'ALERT' ? 'iot-alert-status' : ''}>{sensor.last_reading ?? '—'} {sensor.unit}</b><small>Threshold {sensor.threshold} {sensor.unit}</small></button>)}</div>}
    {selected && <section className="iot-chart-panel"><div className="list-heading"><div><p className="eyebrow">Historical readings / {selected.sensor_code}</p><h3>{selected.sensor_type} trend</h3></div><div className="iot-threshold"><label>Threshold<input type="number" value={thresholds[selected.id] ?? selected.threshold} onChange={(event) => setThresholds((current) => ({ ...current, [selected.id]: event.target.value }))} /></label><button type="button" aria-label="Save threshold" disabled={busy} onClick={() => void saveThreshold(selected)}><Save size={17} /></button></div></div><ResponsiveContainer width="100%" height={280}><LineChart data={chartData}><CartesianGrid stroke="#dfe6df" vertical={false} /><XAxis dataKey="time" tickLine={false} axisLine={false} /><YAxis tickLine={false} axisLine={false} /><Tooltip /><Line type="monotone" dataKey="value" name={selected.unit} stroke={sensorColors[selected.sensor_type] ?? '#31544a'} strokeWidth={3} dot={{ r: 3 }} /><Line type="monotone" dataKey="threshold" name="Threshold" stroke="#b84f45" strokeDasharray="5 5" /></LineChart></ResponsiveContainer></section>}
    <p className="dashboard-disclaimer"><span className="status-dot" />No hardware is connected. Values are simulated for demonstration.</p>
  </div>
}
