import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { useAuth } from '../contexts/useAuth'

type DemoAccount = { label: string; email: string; password: string }

const demoAccounts: DemoAccount[] = [
  { label: 'Administrator', email: 'admin@mineguard.ai', password: 'admin123' },
  { label: 'Mine Manager', email: 'manager@mineguard.ai', password: 'manager123' },
  { label: 'Safety Officer', email: 'safety@mineguard.ai', password: 'safety123' },
  { label: 'Inspector', email: 'inspector@mineguard.ai', password: 'inspector123' },
  { label: 'Contractor', email: 'contractor@mineguard.ai', password: 'contractor123' },
  { label: 'Auditor', email: 'auditor@mineguard.ai', password: 'auditor123' },
]

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('admin@mineguard.ai')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function selectDemoAccount(value: string) {
    const account = demoAccounts.find(({ email: accountEmail }) => accountEmail === value)
    if (account) {
      setEmail(account.email)
      setPassword(account.password)
      setError('')
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)
    try {
      await login(email, password)
      const destination = (location.state as { from?: { pathname?: string } } | null)?.from?.pathname ?? '/'
      navigate(destination, { replace: true })
    } catch {
      setError('Sign-in failed. Check the account details and confirm the API is running.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="login-shell">
      <section className="login-visual" aria-label="MineGuard AI">
        <div className="login-mark">MG</div>
        <p className="eyebrow login-eyebrow">MineGuard AI / secure operations</p>
        <h1>Safety decisions, grounded in the field.</h1>
        <p>Governance, compliance, and incident response for modern coal mine teams.</p>
        <div className="login-visual-footer"><span>SIH 2026</span><span>MITS Gwalior / REBEL TITANS</span></div>
      </section>

      <section className="login-panel">
        <div className="login-card">
          <p className="eyebrow">Operations console</p>
          <h2>Sign in</h2>
          <p className="login-subtitle">Use an authorized MineGuard account to continue.</p>
          <form onSubmit={handleSubmit}>
            <label htmlFor="demo-account">Demo account</label>
            <select id="demo-account" value={email} onChange={(event) => selectDemoAccount(event.target.value)}>
              {demoAccounts.map((account) => <option key={account.email} value={account.email}>{account.label} / {account.email}</option>)}
            </select>
            <label htmlFor="email">Email address</label>
            <input id="email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
            <label htmlFor="password">Password</label>
            <input id="password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
            {error && <p className="login-error" role="alert">{error}</p>}
            <button className="login-button" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Verifying access...' : 'Enter command center'}</button>
          </form>
          <p className="login-mode"><span className="status-dot" />Development environment / AI demo mode</p>
        </div>
      </section>
    </main>
  )
}
