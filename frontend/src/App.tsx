import './App.css'
import { useEffect, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { Activity, AlertTriangle, BarChart3, Bell, CheckCircle2, ClipboardCheck, ClipboardList, FileSearch, FileText, HardHat, LayoutDashboard, Map, Menu, Mountain, Settings, ShieldCheck, Users, X } from 'lucide-react'
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { useAuth } from './contexts/useAuth'
import MinesPage from './pages/MinesPage'
import CompliancePage from './pages/CompliancePage'
import InspectionsPage from './pages/InspectionsPage'
import ViolationsPage from './pages/ViolationsPage'
import CorrectiveActionsPage from './pages/CorrectiveActionsPage'
import ContractorsPage from './pages/ContractorsPage'
import AlertsPage from './pages/AlertsPage'
import AuditTrailPage from './pages/AuditTrailPage'
import AIMonitoringPage from './pages/AIMonitoringPageSelectable'
import RiskAnalyticsPage from './pages/RiskAnalyticsPage'
import DocumentsPage from './pages/DocumentsPage'
import GISMapPage from './pages/GISMapPage'
import IoTMonitoringPage from './pages/IoTMonitoringPage'
import ReportsPage from './pages/ReportsPage'
import { getWorkflowSummary, type WorkflowSummary } from './services/api'

type NavigationItem = {
  label: string
  path: string
  icon: typeof LayoutDashboard
  roles?: string[]
}

const navigationItems: NavigationItem[] = [
  { label: 'Dashboard', path: '/', icon: LayoutDashboard },
  { label: 'Mines', path: '/mines', icon: Mountain },
  { label: 'Compliance', path: '/compliance', icon: ShieldCheck },
  { label: 'Inspections', path: '/inspections', icon: ClipboardCheck },
  { label: 'Violations', path: '/violations', icon: AlertTriangle },
  { label: 'Corrective Actions', path: '/corrective-actions', icon: ClipboardList },
  { label: 'Contractors', path: '/contractors', icon: Users },
  { label: 'AI Monitoring', path: '/ai-monitoring', icon: HardHat },
  { label: 'Risk Analytics', path: '/risk-analytics', icon: BarChart3 },
  { label: 'GIS Map', path: '/gis-map', icon: Map },
  { label: 'IoT Monitoring', path: '/iot-monitoring', icon: Activity },
  { label: 'Documents / OCR', path: '/documents', icon: FileSearch },
  { label: 'Alerts', path: '/alerts', icon: Bell },
  { label: 'Reports', path: '/reports', icon: FileText },
  { label: 'Audit Trail', path: '/audit-trail', icon: ClipboardList, roles: ['ADMIN', 'AUDITOR'] },
  { label: 'Settings', path: '/settings', icon: Settings, roles: ['ADMIN', 'MINE_MANAGER'] },
]

const complianceTrend = [
  { month: 'Apr', rate: 82, target: 90 }, { month: 'May', rate: 85, target: 90 }, { month: 'Jun', rate: 84, target: 90 },
  { month: 'Jul', rate: 88, target: 90 }, { month: 'Aug', rate: 91, target: 90 }, { month: 'Sep', rate: 93, target: 90 },
]
const violationsBySeverity = [{ severity: 'Low', count: 18 }, { severity: 'Medium', count: 11 }, { severity: 'High', count: 7 }, { severity: 'Critical', count: 3 }]
const riskDistribution = [{ name: 'Low', value: 42, color: '#4eac70' }, { name: 'Medium', value: 29, color: '#e4b44c' }, { name: 'High', value: 21, color: '#e17d45' }, { name: 'Critical', value: 8, color: '#b84f45' }]
const inspectionsOverTime = [{ week: 'W1', completed: 18, planned: 22 }, { week: 'W2', completed: 23, planned: 24 }, { week: 'W3', completed: 20, planned: 25 }, { week: 'W4', completed: 28, planned: 28 }]
const contractorCompliance = [{ name: 'Bharat Mine', score: 91 }, { name: 'Eastern IS', score: 76 }, { name: 'KCP Logistics', score: 72 }, { name: 'SafetyWorks', score: 88 }]
const aiEvents = [{ day: 'Mon', ppe: 4, vehicle: 2, zone: 1 }, { day: 'Tue', ppe: 7, vehicle: 3, zone: 2 }, { day: 'Wed', ppe: 5, vehicle: 1, zone: 3 }, { day: 'Thu', ppe: 9, vehicle: 4, zone: 2 }, { day: 'Fri', ppe: 6, vehicle: 3, zone: 1 }, { day: 'Sat', ppe: 3, vehicle: 2, zone: 1 }]
const sensorTrend = [{ time: '06:00', gas: 14, dust: 2.1 }, { time: '09:00', gas: 16, dust: 2.8 }, { time: '12:00', gas: 19, dust: 3.4 }, { time: '15:00', gas: 18, dust: 3.1 }, { time: '18:00', gas: 15, dust: 2.4 }, { time: '21:00', gas: 13, dust: 1.9 }]
const capaStatus = [{ status: 'Open', count: 8 }, { status: 'In progress', count: 13 }, { status: 'Verification', count: 5 }, { status: 'Closed', count: 31 }]

const chartTooltip = { contentStyle: { border: '1px solid #d0dbd1', borderRadius: 0, background: '#f6f8f4', fontSize: 12 }, itemStyle: { color: '#31544a' } }

function KpiCard({ label, value, detail, icon: Icon, tone }: { label: string; value: string; detail: string; icon: typeof ShieldCheck; tone: string }) {
  return <article className="dashboard-kpi"><div className={`kpi-icon ${tone}`}><Icon size={18} /></div><div><span>{label}</span><strong>{value}</strong><small>{detail}</small></div></article>
}

function ChartPanel({ title, subtitle, children, className = '' }: { title: string; subtitle: string; children: React.ReactNode; className?: string }) {
  return <section className={`chart-panel ${className}`}><div className="chart-heading"><div><h3>{title}</h3><p>{subtitle}</p></div><span className="demo-chip">DEMO</span></div><div className="chart-body">{children}</div></section>
}

function App() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [workflowSummary, setWorkflowSummary] = useState<WorkflowSummary | null>(null)
  const visibleNavigation = navigationItems.filter((item) => !item.roles || item.roles.includes(user?.role ?? ''))

  useEffect(() => { void getWorkflowSummary().then(setWorkflowSummary).catch(() => setWorkflowSummary(null)) }, [])

  return (
    <main className="app-shell">
      <button className={`sidebar-scrim ${isSidebarOpen ? 'scrim-open' : ''}`} type="button" aria-label="Close navigation" onClick={() => setIsSidebarOpen(false)} />
      <aside className={`sidebar ${isSidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-heading">
          <div className="brand-mark">MG</div>
          <div>
            <p className="eyebrow">MineGuard</p>
            <p className="brand-name">AI Command</p>
          </div>
          <button className="sidebar-close" type="button" aria-label="Close navigation" onClick={() => setIsSidebarOpen(false)}><X size={18} /></button>
        </div>
        <div className="sidebar-rule" />
        <p className="nav-label">Workspace</p>
        <nav className="primary-navigation" aria-label="Primary navigation">
          {visibleNavigation.map(({ label, path, icon: Icon }) => (
            <NavLink key={path} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} to={path} onClick={() => setIsSidebarOpen(false)}>
              <Icon size={16} strokeWidth={1.8} /><span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <p className="sidebar-foot">SIH 2026 / MITS Gwalior</p>
      </aside>

      <section className="workspace" id="dashboard">
        <header className="topbar">
          <div className="topbar-heading">
            <button className="menu-button" type="button" aria-label="Open navigation" onClick={() => setIsSidebarOpen(true)}><Menu size={20} /></button>
            <div>
            <p className="eyebrow">Governance console / Phase 06</p>
            <h1>Mine safety overview</h1>
            </div>
          </div>
          <div className="session-actions">
            <span className="user-badge">{user?.full_name} / {user?.role.replace('_', ' ')}</span>
            <button className="logout-button" type="button" onClick={() => void logout()}>Sign out</button>
          </div>
        </header>

        <div className="content-grid dashboard-content">
          {location.pathname === '/mines' ? <MinesPage /> : location.pathname === '/compliance' ? <CompliancePage /> : location.pathname === '/inspections' ? <InspectionsPage /> : location.pathname === '/violations' ? <ViolationsPage /> : location.pathname === '/corrective-actions' ? <CorrectiveActionsPage /> : location.pathname === '/contractors' ? <ContractorsPage /> : location.pathname === '/alerts' ? <AlertsPage /> : location.pathname === '/audit-trail' ? <AuditTrailPage /> : location.pathname === '/ai-monitoring' ? <AIMonitoringPage /> : location.pathname === '/risk-analytics' ? <RiskAnalyticsPage /> : location.pathname === '/documents' ? <DocumentsPage /> : location.pathname === '/gis-map' ? <GISMapPage /> : location.pathname === '/iot-monitoring' ? <IoTMonitoringPage /> : location.pathname === '/reports' ? <ReportsPage /> : <>
          <div className="dashboard-heading">
            <div><p className="eyebrow accent">Network command view</p><h2>Good morning, {user?.full_name.split(' ')[0]}.</h2><p>Operational signals across five monitored mine sites.</p></div>
            <div className="dashboard-filters"><span className="date-range">01 Sep - 04 Sep 2026</span><span className="live-chip"><span className="status-dot" />Live snapshot</span></div>
          </div>

          <div className="kpi-grid">
            <KpiCard label="Total mines" value="05" detail="4 active / 1 maintenance" icon={Mountain} tone="green" />
            <KpiCard label="Compliance rate" value="93.2%" detail="+2.1% vs last month" icon={ShieldCheck} tone="blue" />
            <KpiCard label="Open violations" value={workflowSummary ? String(workflowSummary.open_violations) : "39"} detail={workflowSummary ? `${workflowSummary.unread_alerts} unread alerts` : "3 critical / 7 high"} icon={AlertTriangle} tone="red" />
            <KpiCard label="Safety risk score" value="38 / 100" detail="Medium network exposure" icon={BarChart3} tone="amber" />
            <KpiCard label="AI safety events" value={workflowSummary ? String(workflowSummary.ai_events) : "34"} detail={workflowSummary ? `${workflowSummary.risk_events} linked risk events` : "Last 7 days / demo mode"} icon={HardHat} tone="orange" />
            <KpiCard label="Inspection completion" value="87%" detail="96 of 110 planned" icon={ClipboardCheck} tone="teal" />
          </div>

          <div className="chart-grid chart-grid-primary">
            <ChartPanel title="Compliance trend" subtitle="Network score against 90% operating target" className="chart-wide">
              <ResponsiveContainer><LineChart data={complianceTrend}><CartesianGrid stroke="#dfe6df" vertical={false} /><XAxis dataKey="month" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><YAxis domain={[70, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><Tooltip {...chartTooltip} /><Legend iconType="line" wrapperStyle={{ fontSize: 11 }} /><Line type="monotone" dataKey="rate" name="Compliance" stroke="#28564b" strokeWidth={3} dot={{ r: 3, fill: '#f1a24a' }} /><Line type="monotone" dataKey="target" name="Target" stroke="#b8c7bc" strokeDasharray="5 5" /></LineChart></ResponsiveContainer>
            </ChartPanel>
            <ChartPanel title="Risk distribution" subtitle="Current exposure by severity band">
              <ResponsiveContainer><PieChart><Pie data={riskDistribution} dataKey="value" nameKey="name" innerRadius="57%" outerRadius="78%" paddingAngle={3}><Cell fill="#4eac70" /><Cell fill="#e4b44c" /><Cell fill="#e17d45" /><Cell fill="#b84f45" /></Pie><Tooltip {...chartTooltip} /><Legend iconType="circle" wrapperStyle={{ fontSize: 11 }} /></PieChart></ResponsiveContainer>
            </ChartPanel>
          </div>

          <div className="chart-grid">
            <ChartPanel title="Violations by severity" subtitle="Open and in-progress findings"><ResponsiveContainer><BarChart data={violationsBySeverity} layout="vertical"><CartesianGrid stroke="#dfe6df" horizontal={false} /><XAxis type="number" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><YAxis dataKey="severity" type="category" width={58} tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><Tooltip {...chartTooltip} /><Bar dataKey="count" name="Findings" fill="#e17d45" barSize={18} radius={[0, 2, 2, 0]} /></BarChart></ResponsiveContainer></ChartPanel>
            <ChartPanel title="Inspections over time" subtitle="Planned versus completed rounds"><ResponsiveContainer><AreaChart data={inspectionsOverTime}><CartesianGrid stroke="#dfe6df" vertical={false} /><XAxis dataKey="week" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><Tooltip {...chartTooltip} /><Legend iconType="line" wrapperStyle={{ fontSize: 11 }} /><Area type="monotone" dataKey="planned" name="Planned" stroke="#b8c7bc" fill="#e7eee8" /><Area type="monotone" dataKey="completed" name="Completed" stroke="#28564b" fill="#b9d3c2" /></AreaChart></ResponsiveContainer></ChartPanel>
            <ChartPanel title="Contractor compliance" subtitle="Current partner scores"><ResponsiveContainer><BarChart data={contractorCompliance}><CartesianGrid stroke="#dfe6df" vertical={false} /><XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 10, fill: '#71827b' }} /><YAxis domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><Tooltip {...chartTooltip} /><Bar dataKey="score" name="Score" fill="#4eac70" barSize={24} radius={[2, 2, 0, 0]} /></BarChart></ResponsiveContainer></ChartPanel>
          </div>

          <div className="chart-grid">
            <ChartPanel title="AI safety events" subtitle="Detection volume by event class"><ResponsiveContainer><BarChart data={aiEvents}><CartesianGrid stroke="#dfe6df" vertical={false} /><XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><Tooltip {...chartTooltip} /><Legend iconType="rect" wrapperStyle={{ fontSize: 11 }} /><Bar dataKey="ppe" name="PPE" stackId="events" fill="#e17d45" /><Bar dataKey="vehicle" name="Vehicle" stackId="events" fill="#e4b44c" /><Bar dataKey="zone" name="Zone" stackId="events" fill="#4eac70" /></BarChart></ResponsiveContainer></ChartPanel>
            <ChartPanel title="IoT sensor trend" subtitle="Simulated gas ppm and dust mg/m3"><ResponsiveContainer><LineChart data={sensorTrend}><CartesianGrid stroke="#dfe6df" vertical={false} /><XAxis dataKey="time" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><YAxis yAxisId="left" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><Tooltip {...chartTooltip} /><Legend iconType="line" wrapperStyle={{ fontSize: 11 }} /><Line yAxisId="left" type="monotone" dataKey="gas" name="Gas ppm" stroke="#b84f45" strokeWidth={2} /><Line yAxisId="left" type="monotone" dataKey="dust" name="Dust mg/m3" stroke="#e4b44c" strokeWidth={2} /></LineChart></ResponsiveContainer></ChartPanel>
            <ChartPanel title="Corrective action status" subtitle="CAPA queue across all sites"><ResponsiveContainer><BarChart data={capaStatus}><CartesianGrid stroke="#dfe6df" vertical={false} /><XAxis dataKey="status" tickLine={false} axisLine={false} tick={{ fontSize: 10, fill: '#71827b' }} /><YAxis tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#71827b' }} /><Tooltip {...chartTooltip} /><Bar dataKey="count" name="Actions" fill="#28564b" barSize={30} radius={[2, 2, 0, 0]} /></BarChart></ResponsiveContainer></ChartPanel>
          </div>

          <div className="dashboard-bottom-grid">
            <section className="dashboard-list-panel"><div className="list-heading"><div><p className="eyebrow">Attention queue</p><h3>Priority alerts</h3></div><NavLink to="/alerts">View all</NavLink></div><div className="alert-list"><div className="alert-row"><span className="alert-severity critical">CRITICAL</span><div><strong>Gas threshold approaching</strong><small>Gevra Central Block / Processing Area</small></div><time>08 min</time></div><div className="alert-row"><span className="alert-severity high">HIGH</span><div><strong>PPE violation detected</strong><small>Kusmunda North / Main Haul Road</small></div><time>18 min</time></div><div className="alert-row"><span className="alert-severity medium">MEDIUM</span><div><strong>Compliance verification overdue</strong><small>Raniganj Safety Pilot / Statutory review</small></div><time>42 min</time></div></div></section>
            <section className="dashboard-list-panel"><div className="list-heading"><div><p className="eyebrow">System log</p><h3>Recent activity</h3></div><NavLink to="/audit-trail">Audit trail</NavLink></div><div className="activity-list"><div><CheckCircle2 size={16} /><p><strong>Inspection submitted</strong><span>Daily transport safety / INS-2026-0001</span></p><time>12:14</time></div><div><HardHat size={16} /><p><strong>AI event linked</strong><span>No helmet event / CAM-HAUL-01</span></p><time>11:56</time></div><div><ClipboardList size={16} /><p><strong>CAPA assigned</strong><span>CAPA-2026-0001 to Bharat Mine Services</span></p><time>11:42</time></div></div></section>
          </div>
          <p className="dashboard-disclaimer"><span className="status-dot" />Workflow KPIs include live persisted AI, risk, violation, alert, and CAPA records; chart trends remain demo data.</p>
          </>}
        </div>
      </section>
    </main>
  )
}

export default App
