import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import {
  LayoutDashboard,
  Users,
  Mail,
  Send,
  Settings,
  LogOut,
  Menu,
  X,
} from 'lucide-react'
import { useState } from 'react'

const navigation = [
  { name: '儀表板', href: '/', icon: LayoutDashboard },
  { name: '供應商', href: '/suppliers', icon: Users },
  { name: '活動', href: '/campaigns', icon: Send },
  { name: '郵件', href: '/emails', icon: Mail },
  { name: '設置', href: '/settings', icon: Settings },
]

export function Layout() {
  const location = useLocation()
  const { user, logout } = useAuth()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Mobile sidebar */}
      <div className={`fixed inset-0 z-50 lg:hidden ${sidebarOpen ? 'block' : 'hidden'}`}>
        <div className="fixed inset-0 bg-gray-900/50" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 w-64 bg-white dark:bg-gray-800">
          <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200 dark:border-gray-700">
            <span className="text-xl font-bold text-primary-600">AI LeadGen</span>
            <button onClick={() => setSidebarOpen(false)}>
              <X className="w-6 h-6" />
            </button>
          </div>
          <nav className="mt-6 px-4 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/50 dark:text-primary-400'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-1 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
          <div className="flex items-center h-16 px-6 border-b border-gray-200 dark:border-gray-700">
            <span className="text-xl font-bold text-primary-600">AI LeadGen</span>
          </div>
          <nav className="flex-1 px-4 py-6 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-3 text-sm font-medium rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-600 dark:bg-primary-900/50 dark:text-primary-400'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </Link>
              )
            })}
          </nav>
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                  <span className="text-sm font-medium text-primary-600">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {user?.email}
                </p>
              </div>
              <button
                onClick={logout}
                className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        <div className="sticky top-0 z-40 flex items-center h-16 px-4 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 lg:px-8">
          <button
            className="lg:hidden p-2 text-gray-600 dark:text-gray-400"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="w-6 h-6" />
          </button>
        </div>
        <main className="py-6 px-4 sm:px-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
