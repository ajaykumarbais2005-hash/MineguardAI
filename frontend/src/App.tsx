import './App.css'
import './design-system.css'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, Navigate, NavLink, useLocation } from 'react-router-dom'
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bell,
  CheckCircle2,
  ClipboardCheck,
  ClipboardList,
  FileSearch,
  FileText,
  HardHat,
  LayoutDashboard,
  Map,
  Menu,
  Mountain,
  Settings,
  ShieldCheck,
  Users,
  X,
  type LucideIcon,
} from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
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
import {
  getAlertSummary,
  getComplianceSummary,
  listAlerts,
  listInspections,
  listMines,
  listRiskEvents,
  listViolations,
  type Alert,
  type AlertSummary,
  type ComplianceSummary,
  type Inspection,
  type Mine,
  type RiskEvent,
  type Violation,
} from './services/api'

type NavigationItem = {
  label: string
  path: string
  icon: LucideIcon
  roles?: string[]
}

type DashboardData = {
  mines: Mine[]
  inspections: Inspection[]
  violations: Violation[]
  riskEvents: RiskEvent[]
  compliance: ComplianceSummary
  alerts: Alert[]
  alertSummary: AlertSummary
}

type ActivityItem = {
  title: string
  description: string
  date: string
  path: string
  icon: LucideIcon
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

const riskColors: Record<string, string> = {
  LOW: '#16805d',
  MEDIUM: '#b7791f',
  HIGH: '#d05b24',
  CRITICAL: '#c43d3d',
}

const chartTooltip = {
  contentStyle: {
    border: '1px solid #d6dee8',
    borderRadius: 8,
    background: '#ffffff',
    fontSize: 12,
    boxShadow: '0 8px 24px #172b4d18',
  },
  itemStyle: { color: '#25364b' },
}

function KpiCard({ label, value, detail, icon: Icon, tone }: {
  label: string
  value: string
  detail: string
  icon: LucideIcon
  tone: string
}) {
  return (
    <article className="dashboard-kpi">
      <div className={`kpi-icon ${tone}`} aria-hidden="true"><Icon size={18} /></div>
      <div className="kpi-copy">
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
    </article>
  )
}

function ChartPanel({ title, subtitle, children }: {
  title: string
  subtitle: string
  children: React.ReactNode
}) {
  return (
    <section className="chart-panel">
      <div className="chart-heading">
        <div><h3>{title}</h3><p>{subtitle}</p></div>
        <span className="data-source-chip">API DATA</span>
      </div>
      <div className="chart-body">{children}</div>
    </section>
  )
}

function EmptyChart() {
  return <div className="chart-empty">No records available for this view yet.</div>
}

function Dashboard({ data, isLoading, error, onRetry, firstName }: {
  data: DashboardData | null
  isLoading: boolean
  error: string
  onRetry: () => void
  firstName: string
}) {
  const activeInspections = data?.inspections.filter((inspection) => ['DRAFT', 'IN_PROGRESS'].includes(inspection.status)).length ?? 0
  const activeMines = data?.mines.filter((mine) => mine.status === 'ACTIVE').length ?? 0
  const criticalRisks = data?.riskEvents.filter((event) => event.level.toUpperCase() === 'CRITICAL').length ?? 0
  const compliancePercent = data && data.compliance.total > 0
    ? Math.round((data.compliance.compliant / data.compliance.total) * 100)
    : null
  const activeAlerts = data ? data.alertSummary.unread + data.alertSummary.acknowledged : 0

  const riskDistribution = useMemo(() => {
    const levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    return levels.map((level) => ({
      name: level.charAt(0) + level.slice(1).toLowerCase(),
      value: data?.riskEvents.filter((event) => event.level.toUpperCase() === level).length ?? 0,
      color: riskColors[level],
    }))
  }, [data])

  const violationCounts = useMemo(() => {
    const levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    return levels.map((severity) => ({
      severity: severity.charAt(0) + severity.slice(1).toLowerCase(),
      count: data?.violations.filter((violation) => violation.severity.toUpperCase() === severity).length ?? 0,
    }))
  }, [data])

  const inspectionCounts = useMemo(() => {
    const statuses = ['DRAFT', 'IN_PROGRESS', 'SUBMITTED', 'REVIEWED', 'CLOSED']
    return statuses.map((status) => ({
      status: status.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase()),
      count: data?.inspections.filter((inspection) => inspection.status === status).length ?? 0,
    }))
  }, [data])

  const recentActivities = useMemo<ActivityItem[]>(() => {
    if (!data) return []
    const entries: Array<ActivityItem & { timestamp: number }> = [
      ...data.alerts.map((alert) => ({
        title: `Alert ${alert.status.toLowerCase()}`,
        description: `${alert.alert_type.replaceAll('_', ' ')} / ${alert.mine_name}`,
        date: new Date(alert.created_at).toLocaleString('en-IN'),
        timestamp: new Date(alert.created_at).getTime(),
        path: '/alerts',
        icon: Bell,
      })),
      ...data.violations.map((violation) => ({
        title: `Violation ${violation.status.toLowerCase().replaceAll('_', ' ')}`,
        description: `${violation.violation_code} / ${violation.mine_name}`,
        date: new Date(violation.detected_at).toLocaleString('en-IN'),
        timestamp: new Date(violation.detected_at).getTime(),
        path: '/violations',
        icon: AlertTriangle,
      })),
      ...data.inspections.map((inspection) => ({
        title: `Inspection ${inspection.status.toLowerCase().replaceAll('_', ' ')}`,
        description: `${inspection.checklist_name} / ${inspection.mine_name}`,
        date: new Date(inspection.submitted_at ?? inspection.started_at).toLocaleString('en-IN'),
        timestamp: new Date(inspection.submitted_at ?? inspection.started_at).getTime(),
        path: '/inspections',
        icon: ClipboardCheck,
      })),
    ]
    return entries
      .filter((entry) => Number.isFinite(entry.timestamp))
      .sort((left, right) => right.timestamp - left.timestamp)
      .slice(0, 5)
  }, [data])

  return (
    <>
      <div className="dashboard-heading">
        <div>
          <p className="eyebrow accent">Operational overview</p>
          <h2>Welcome back, {firstName}.</h2>
          <p>Current safety and compliance signals from the MineGuard API.</p>
        </div>
        <span className="live-chip"><span className="status-dot" />Live API data</span>
      </div>

      {error && <div className="module-error dashboard-error" role="alert">
        <span>{error}</span><button type="button" className="secondary-action" onClick={onRetry}>Retry</button>
      </div>}

      {isLoading ? (
        <div className="kpi-grid" aria-label="Loading dashboard data" aria-busy="true">
          {Array.from({ length: 6 }, (_, index) => <div className="dashboard-kpi dashboard-kpi-skeleton" key={index}><span /><span /><span /></div>)}
        </div>
      ) : data ? (
        <>
          <div className="kpi-grid">
            <KpiCard label="Total mines" value={String(data.mines.length)} detail={`${activeMines} active sites`} icon={Mountain} tone="green" />
            <KpiCard label="Active inspections" value={String(activeInspections)} detail={`${data.inspections.length} records`} icon={ClipboardCheck} tone="blue" />
            <KpiCard label="Open violations" value={String(data.violations.filter((item) => !['RESOLVED', 'VERIFIED', 'CLOSED'].includes(item.status)).length)} detail={`${data.violations.length} total records`} icon={AlertTriangle} tone="red" />
            <KpiCard label="Critical risks" value={String(criticalRisks)} detail={`${data.riskEvents.length} risk events`} icon={ShieldCheck} tone="amber" />
            <KpiCard label="Compliant requirements" value={compliancePercent === null ? '—' : `${compliancePercent}%`} detail={`${data.compliance.compliant} of ${data.compliance.total} fully compliant`} icon={CheckCircle2} tone="teal" />
            <KpiCard label="Active alerts" value={String(activeAlerts)} detail={`${data.alertSummary.unread} unread`} icon={Bell} tone="orange" />
          </div>

          <div className="dashboard-safety-strip">
            <div><span className="eyebrow">Mine safety overview</span><strong>{activeMines} of {data.mines.length} sites active</strong></div>
            <div><span>High-risk sites</span><strong>{data.mines.filter((mine) => ['HIGH', 'CRITICAL'].includes(mine.risk_level.toUpperCase())).length}</strong></div>
            <div><span>Overdue compliance</span><strong>{data.compliance.overdue}</strong></div>
            <Link to="/mines">View mine register</Link>
          </div>

          <div className="chart-grid chart-grid-primary">
            <ChartPanel title="Risk distribution" subtitle="Recorded risk events by assessed level">
              {data.riskEvents.length === 0 ? <EmptyChart /> : <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={riskDistribution} dataKey="value" nameKey="name" innerRadius="58%" outerRadius="78%" paddingAngle={3}>
                    {riskDistribution.map((entry) => <Cell key={entry.name} fill={entry.color} />)}
                  </Pie>
                  <Tooltip {...chartTooltip} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>}
            </ChartPanel>
            <ChartPanel title="Violations by severity" subtitle="Current violation register, grouped by severity">
              {data.violations.length === 0 ? <EmptyChart /> : <ResponsiveContainer width="100%" height="100%">
                <BarChart data={violationCounts} layout="vertical" margin={{ left: 4, right: 12 }}>
                  <CartesianGrid stroke="#e8edf3" horizontal={false} />
                  <XAxis type="number" allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#61738a' }} />
                  <YAxis dataKey="severity" type="category" width={64} tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#61738a' }} />
                  <Tooltip {...chartTooltip} />
                  <Bar dataKey="count" name="Violations" fill="#d05b24" radius={[0, 5, 5, 0]} />
                </BarChart>
              </ResponsiveContainer>}
            </ChartPanel>
          </div>

          <div className="chart-grid chart-grid-secondary">
            <ChartPanel title="Inspection status" subtitle="Records currently in the inspection workflow">
              {data.inspections.length === 0 ? <EmptyChart /> : <ResponsiveContainer width="100%" height="100%">
                <BarChart data={inspectionCounts} margin={{ left: 0, right: 12 }}>
                  <CartesianGrid stroke="#e8edf3" vertical={false} />
                  <XAxis dataKey="status" tickLine={false} axisLine={false} tick={{ fontSize: 10, fill: '#61738a' }} />
                  <YAxis allowDecimals={false} tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#61738a' }} />
                  <Tooltip {...chartTooltip} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="count" name="Inspections" fill="#2563a6" radius={[5, 5, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>}
            </ChartPanel>
            <section className="dashboard-list-panel">
              <div className="list-heading"><div><p className="eyebrow">Live register</p><h3>Priority alerts</h3></div><Link to="/alerts">View all</Link></div>
              {!data.alerts.length ? <p className="inspection-empty">No alerts have been recorded.</p> : <div className="alert-list">
                {data.alerts.slice(0, 4).map((alert) => <div className="alert-row" key={alert.id}>
                  <span className={`alert-severity ${alert.severity.toLowerCase()}`}>{alert.severity}</span>
                  <div><strong>{alert.message}</strong><small>{alert.mine_name} / {alert.zone_name ?? 'All zones'}</small></div>
                  <time>{new Date(alert.created_at).toLocaleDateString('en-IN')}</time>
                </div>)}
              </div>}
            </section>
            <section className="dashboard-list-panel">
              <div className="list-heading"><div><p className="eyebrow">Recent records</p><h3>Recent activity</h3></div><Link to="/violations">Open register</Link></div>
              {!recentActivities.length ? <p className="inspection-empty">No recent records are available.</p> : <div className="activity-list">
                {recentActivities.map((item, index) => {
                  const Icon = item.icon
                  return <div key={`${item.path}-${item.title}-${index}`}>
                    <Icon size={16} aria-hidden="true" />
                    <p><strong>{item.title}</strong><span>{item.description}</span></p>
                    <time>{item.date}</time>
                  </div>
                })}
              </div>}
            </section>
          </div>
          <p className="dashboard-disclaimer">Dashboard figures are derived from persisted API records; development environments may include seeded demonstration data.</p>
        </>
      ) : null}
    </>
  )
}

function App() {
  const { user, logout } = useAuth()
  const location = useLocation()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [dashboardLoading, setDashboardLoading] = useState(true)
  const [dashboardError, setDashboardError] = useState('')
  const [unreadAlertCount, setUnreadAlertCount] = useState<number | null>(null)
  const [logoutError, setLogoutError] = useState('')
  const visibleNavigation = navigationItems.filter((item) => !item.roles || item.roles.includes(user?.role ?? ''))
  const restrictedPage = navigationItems.find(
    (item) => item.path === location.pathname && item.roles && !item.roles.includes(user?.role ?? ''),
  )
  const currentPage = navigationItems.find((item) => item.path === location.pathname)
  const isDashboard = location.pathname === '/'
    || location.pathname === '/settings'
    || !navigationItems.some((item) => item.path === location.pathname)

  const loadDashboard = useCallback(async () => {
    setDashboardLoading(true)
    setDashboardError('')
    try {
      const [mines, inspections, violations, riskEvents, compliance, alerts, alertSummary] = await Promise.all([
        listMines(),
        listInspections(),
        listViolations(),
        listRiskEvents(),
        getComplianceSummary(),
        listAlerts(),
        getAlertSummary(),
      ])
      setDashboardData({ mines, inspections, violations, riskEvents, compliance, alerts, alertSummary })
      setUnreadAlertCount(alertSummary.unread)
    } catch {
      setDashboardError('Dashboard data could not be loaded. Check the API connection and try again.')
    } finally {
      setDashboardLoading(false)
    }
  }, [])

  useEffect(() => {
    if (isDashboard) {
      void loadDashboard()
      return
    }

    let active = true
    void getAlertSummary()
      .then((summary) => {
        if (active) setUnreadAlertCount(summary.unread)
      })
      .catch(() => {
        if (active) setUnreadAlertCount(null)
      })
    return () => { active = false }
  }, [isDashboard, loadDashboard])
  useEffect(() => { setIsSidebarOpen(false) }, [location.pathname])
  useEffect(() => {
    function closeOnEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') setIsSidebarOpen(false)
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [])

  async function handleLogout() {
    setLogoutError('')
    try {
      await logout()
    } catch {
      setLogoutError('The server could not confirm sign-out. Your local session has been cleared.')
    }
  }

  if (restrictedPage) {
    return <Navigate to="/" replace />
  }

  return (
    <main className="app-shell">
      <button
        className={`sidebar-scrim ${isSidebarOpen ? 'scrim-open' : ''}`}
        type="button"
        aria-label="Close navigation"
        aria-hidden={!isSidebarOpen}
        tabIndex={isSidebarOpen ? 0 : -1}
        onClick={() => setIsSidebarOpen(false)}
      />
      <aside className={`sidebar ${isSidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-heading">
          <div className="brand-mark" aria-hidden="true">MG</div>
          <div>
            <p className="eyebrow">MineGuard AI</p>
            <p className="brand-name">Safety operations</p>
          </div>
          <button className="sidebar-close" type="button" aria-label="Close navigation" onClick={() => setIsSidebarOpen(false)}><X size={18} /></button>
        </div>
        <div className="sidebar-rule" />
        <p className="nav-label">Workspace</p>
        <nav className="primary-navigation" aria-label="Primary navigation">
          {visibleNavigation.map(({ label, path, icon: Icon }) => (
            <NavLink key={path} end={path === '/'} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} to={path} onClick={() => setIsSidebarOpen(false)}>
              <Icon size={17} strokeWidth={1.8} aria-hidden="true" /><span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <p className="sidebar-foot">REBEL TITANS <span>MITS Gwalior · SIH 2026</span></p>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="topbar-heading">
            <button
              className="menu-button"
              type="button"
              aria-label={isSidebarOpen ? 'Close navigation' : 'Open navigation'}
              aria-expanded={isSidebarOpen}
              onClick={() => setIsSidebarOpen((open) => !open)}
            ><Menu size={20} /></button>
            <div>
              <p className="eyebrow">MineGuard AI / Safety operations</p>
              <h1>{currentPage?.label ?? 'Dashboard'}</h1>
            </div>
          </div>
          <div className="session-actions">
            <NavLink to="/alerts" className="notification-link" aria-label="View active alerts">
              <Bell size={18} /><span>Alerts</span>
              {unreadAlertCount !== null && unreadAlertCount > 0 && <b>{unreadAlertCount}</b>}
            </NavLink>
            <span className="user-badge"><span className="profile-initial">{user?.full_name.charAt(0).toUpperCase()}</span><span>{user?.full_name}<small>{user?.role.replaceAll('_', ' ')}</small></span></span>
            <button className="logout-button" type="button" onClick={() => void handleLogout()}>Sign out</button>
          </div>
        </header>
        {logoutError && <p className="module-error logout-message" role="status">{logoutError}</p>}

        <div className="content-grid dashboard-content">
          {isDashboard ? (
            <Dashboard
              data={dashboardData}
              isLoading={dashboardLoading}
              error={dashboardError}
              onRetry={() => void loadDashboard()}
              firstName={user?.full_name.split(' ')[0] ?? 'there'}
            />
          ) : location.pathname === '/mines' ? <MinesPage />
            : location.pathname === '/compliance' ? <CompliancePage />
              : location.pathname === '/inspections' ? <InspectionsPage />
                : location.pathname === '/violations' ? <ViolationsPage />
                  : location.pathname === '/corrective-actions' ? <CorrectiveActionsPage />
                    : location.pathname === '/contractors' ? <ContractorsPage />
                      : location.pathname === '/alerts' ? <AlertsPage />
                        : location.pathname === '/audit-trail' ? <AuditTrailPage />
                          : location.pathname === '/ai-monitoring' ? <AIMonitoringPage />
                            : location.pathname === '/risk-analytics' ? <RiskAnalyticsPage />
                              : location.pathname === '/documents' ? <DocumentsPage />
                                : location.pathname === '/gis-map' ? <GISMapPage />
                                  : location.pathname === '/iot-monitoring' ? <IoTMonitoringPage />
                                    : location.pathname === '/reports' ? <ReportsPage />
                                      : <Dashboard data={dashboardData} isLoading={dashboardLoading} error={dashboardError} onRetry={() => void loadDashboard()} firstName={user?.full_name.split(' ')[0] ?? 'there'} />}
        </div>
      </section>
    </main>
  )
}

export default App
