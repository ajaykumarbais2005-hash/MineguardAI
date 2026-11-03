import { useState, type FormEvent } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, LoaderCircle } from 'lucide-react'

import { useAuth } from '../contexts/useAuth'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isPasswordVisible, setIsPasswordVisible] = useState(false)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

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
            <label htmlFor="email">Email address</label>
            <input id="email" type="email" autoComplete="username" autoCapitalize="none" maxLength={254} value={email} onChange={(event) => { setEmail(event.target.value); setError('') }} required />
            <label htmlFor="password">Password</label>
            <div className="login-password-field">
              <input id="password" type={isPasswordVisible ? 'text' : 'password'} autoComplete="current-password" maxLength={72} value={password} onChange={(event) => { setPassword(event.target.value); setError('') }} required />
              <button
                className="password-visibility"
                type="button"
                aria-label={isPasswordVisible ? 'Hide password' : 'Show password'}
                aria-pressed={isPasswordVisible}
                onClick={() => setIsPasswordVisible((visible) => !visible)}
              >
                {isPasswordVisible ? <EyeOff size={17} /> : <Eye size={17} />}
              </button>
            </div>
            {error && <p className="login-error" role="alert">{error}</p>}
            <button className="login-button" type="submit" disabled={isSubmitting}>{isSubmitting ? <><LoaderCircle size={16} className="loading-icon" />Verifying access...</> : 'Sign in securely'}</button>
          </form>
          <p className="login-mode"><span className="status-dot" />Development environment / AI demo mode</p>
        </div>
      </section>
    </main>
  )
}
