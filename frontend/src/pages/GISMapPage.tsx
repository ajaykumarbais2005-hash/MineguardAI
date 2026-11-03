import type { ComponentType, ReactNode } from 'react'
import { useEffect, useState } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet'
import { getGISMap, type GISPoint } from '../services/api'

type MapProps = { center: [number, number]; zoom: number; scrollWheelZoom?: boolean; className?: string; children?: ReactNode }
type TileProps = { attribution: string; url: string }
type CircleProps = { center: [number, number]; radius: number; pathOptions: { color: string; fillColor: string; fillOpacity: number }; children?: ReactNode }

const TypedMapContainer = MapContainer as unknown as ComponentType<MapProps>
const TypedTileLayer = TileLayer as unknown as ComponentType<TileProps>
const TypedCircleMarker = CircleMarker as unknown as ComponentType<CircleProps>

const kinds = ['ALL', 'MINE', 'ZONE', 'CAMERA', 'SENSOR', 'RISK', 'VIOLATION', 'ALERT']
const colors: Record<string, string> = { MINE: '#28564b', ZONE: '#4eac70', CAMERA: '#3c78a8', SENSOR: '#e4b44c', RISK: '#b84f45', VIOLATION: '#e17d45', ALERT: '#8e4d87' }

export default function GISMapPage() {
  const [points, setPoints] = useState<GISPoint[]>([])
  const [filter, setFilter] = useState('ALL')
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadMap() {
      try {
        setPoints((await getGISMap()).points)
      } catch {
        setError('GIS data could not be loaded. Confirm the backend is available.')
      } finally {
        setIsLoading(false)
      }
    }
    void loadMap()
  }, [])

  const visiblePoints = filter === 'ALL' ? points : points.filter((point) => point.kind === filter)
  const center: [number, number] = points[0] ? [points[0].latitude, points[0].longitude] : [22.353, 82.686]

  return <div className="gis-management">
    <div className="module-heading"><div><p className="eyebrow accent">Spatial command / Phase 19</p><h2>GIS Map</h2><p>Inspect mine assets, risk areas, violations, alerts, and sensors on an OpenStreetMap view.</p></div><span className="demo-chip">OPENSTREETMAP</span></div>
    <div className="gis-toolbar"><span>{isLoading ? <span className="module-loading" role="status">Loading map data…</span> : <><strong>{visiblePoints.length}</strong> mapped points</>}</span><select aria-label="Filter map points" value={filter} onChange={(event) => setFilter(event.target.value)}>{kinds.map((kind) => <option key={kind} value={kind}>{kind === 'ALL' ? 'All layers' : kind}</option>)}</select><span className="gis-mode">{points.some((point) => point.demo_position) ? 'Some positions are demo offsets' : 'Coordinate data'}</span></div>
    {error && <p className="module-error" role="alert">{error}</p>}
    <section className="gis-map-panel"><TypedMapContainer center={center} zoom={9} scrollWheelZoom className="gis-map"><TypedTileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />{visiblePoints.map((point) => <TypedCircleMarker key={point.id} center={[point.latitude, point.longitude]} radius={point.kind === 'MINE' ? 10 : 7} pathOptions={{ color: colors[point.kind] ?? '#31544a', fillColor: colors[point.kind] ?? '#31544a', fillOpacity: .78 }}><Popup><strong>{point.label}</strong><br />{point.kind}{point.risk_level ? ` / ${point.risk_level}` : ''}{point.status ? ` / ${point.status}` : ''}{point.demo_position && <><br /><small>Demo-positioned from mine coordinates</small></>}</Popup></TypedCircleMarker>)}</TypedMapContainer></section>
    <section className="gis-legend"><div><strong>Map layers</strong><span>Interactive operational context</span></div>{Object.entries(colors).map(([kind, color]) => <span key={kind}><i style={{ backgroundColor: color }} />{kind}</span>)}</section>
  </div>
}
