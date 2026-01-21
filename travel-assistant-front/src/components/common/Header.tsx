import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store'

export const Header = () => {
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const appName = import.meta.env.VITE_APP_NAME || '旅游助手'

  return (
    <header className="sticky top-0 z-20 border-b border-indigo-100 bg-white/70 backdrop-blur">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-2xl bg-indigo-600 text-white shadow-sm shadow-indigo-200/60">
              🌍
            </div>
            <span className="text-lg font-semibold text-gray-900">{appName}</span>
          </Link>

          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors">
              对话
            </Link>
          </nav>

          <div className="flex items-center space-x-3">
            {isAuthenticated && user ? (
              <>
                <span className="hidden sm:inline text-sm text-gray-700">欢迎，{user.name}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 rounded-xl border border-gray-200 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-all"
                >
                  退出登录
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors"
                >
                  登录
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-xl bg-indigo-600 text-sm font-semibold text-white hover:bg-indigo-700 transition-colors"
                >
                  注册
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
