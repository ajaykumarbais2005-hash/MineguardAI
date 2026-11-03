import { CalendarDays, ShieldCheck, UserRound } from 'lucide-react'
import { useAuth } from '../contexts/useAuth'

export default function SettingsPage() {
  const { user } = useAuth()

  return (
    <div className="settings-management">
      <div className="module-heading">
        <div>
          <h2>Account settings</h2>
          <p>Review your MineGuard account details and access status.</p>
        </div>
      </div>

      <section className="settings-card" aria-labelledby="account-details-heading">
        <div className="settings-card-heading">
          <span className="settings-icon"><UserRound size={19} aria-hidden="true" /></span>
          <div>
            <h3 id="account-details-heading">Account details</h3>
            <p>Your profile information currently associated with this account.</p>
          </div>
        </div>
        <dl className="settings-details">
          <div>
            <dt>Full name</dt>
            <dd>{user?.full_name ?? 'Not available'}</dd>
          </div>
          <div>
            <dt>Email address</dt>
            <dd>{user?.email ?? 'Not available'}</dd>
          </div>
          <div>
            <dt>Account role</dt>
            <dd>{user?.role.replaceAll('_', ' ') ?? 'Not available'}</dd>
          </div>
          <div>
            <dt>Member since</dt>
            <dd className="settings-value-with-icon">
              <CalendarDays size={15} aria-hidden="true" />
              {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-IN', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
              }) : 'Not available'}
            </dd>
          </div>
        </dl>
      </section>

      <section className="settings-card settings-access-card" aria-labelledby="access-status-heading">
        <div className="settings-card-heading">
          <span className="settings-icon"><ShieldCheck size={19} aria-hidden="true" /></span>
          <div>
            <h3 id="access-status-heading">Access status</h3>
            <p>Your account access is managed by your assigned MineGuard role.</p>
          </div>
        </div>
        <div className="settings-access-status">
          <span className={`settings-status-badge ${user?.is_active ? 'is-active' : 'is-inactive'}`}>
            <span aria-hidden="true" />
            {user?.is_active ? 'Active' : 'Inactive'}
          </span>
          <span className="settings-access-note">
            Permissions are based on your account role. Contact your administrator if your access needs to change.
          </span>
        </div>
      </section>
    </div>
  )
}
