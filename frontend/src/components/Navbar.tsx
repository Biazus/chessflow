import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Navbar.css'

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <h1>♟️ ChessFlow</h1>
        </div>

        <div className="navbar-content">
          <div className="navbar-user">
            {user && (
              <>
                <span className="user-info">
                  {user.full_name || user.username} • {user.elo_rating} ELO
                </span>
                <button onClick={handleLogout} className="btn-logout">
                  Sair
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}