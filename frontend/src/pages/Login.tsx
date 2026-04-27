import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { Link } from 'react-router-dom'

export function Login() {
  const { login, register } = useAuth()
  const [isRegister, setIsRegister] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: '',
    company_name: '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      if (isRegister) {
        await register(formData)
      } else {
        await login(formData.username, formData.password)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h1 className="text-center text-3xl font-bold text-primary-600">AI LeadGen</h1>
          <h2 className="mt-6 text-center text-2xl font-bold text-gray-900 dark:text-white">
            {isRegister ? '創建帳戶' : '登入您的帳戶'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
            {isRegister ? '已經有帳戶了？' : '還沒有帳戶？'}
            <button
              onClick={() => setIsRegister(!isRegister)}
              className="font-medium text-primary-600 hover:text-primary-500 ml-1"
            >
              {isRegister ? '立即登入' : '立即註冊'}
            </button>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {isRegister && (
              <>
                <div>
                  <label htmlFor="email" className="label">電子郵件</label>
                  <input
                    id="email"
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="input"
                    placeholder="your@email.com"
                  />
                </div>
                <div>
                  <label htmlFor="full_name" className="label">姓名</label>
                  <input
                    id="full_name"
                    type="text"
                    value={formData.full_name}
                    onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                    className="input"
                    placeholder="您的姓名"
                  />
                </div>
                <div>
                  <label htmlFor="company_name" className="label">公司名稱</label>
                  <input
                    id="company_name"
                    type="text"
                    value={formData.company_name}
                    onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                    className="input"
                    placeholder="您的公司"
                  />
                </div>
              </>
            )}
            <div>
              <label htmlFor="username" className="label">
                {isRegister ? '用戶名' : '用戶名或電子郵件'}
              </label>
              <input
                id="username"
                type="text"
                required
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="input"
                placeholder="username"
              />
            </div>
            <div>
              <label htmlFor="password" className="label">密碼</label>
              <input
                id="password"
                type="password"
                required
                minLength={8}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="input"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                處理中...
              </span>
            ) : (
              isRegister ? '創建帳戶' : '登入'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
