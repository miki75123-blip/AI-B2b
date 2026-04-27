import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import toast from 'react-hot-toast'
import { Save, Key, Mail, User } from 'lucide-react'

export function Settings() {
  const { user } = useAuth()
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    company_name: user?.company_name || '',
    sendgrid_api_key: '',
    email_from_address: '',
    email_from_name: '',
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    
    try {
      // API call would go here
      toast.success('設置已保存')
    } catch (error) {
      toast.error('保存失敗')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">設置</h1>
        <p className="text-gray-600 dark:text-gray-400">管理您的帳戶和應用程序設置</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Profile */}
        <div className="card">
          <div className="flex items-center mb-4">
            <User className="w-5 h-5 text-gray-400 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              個人資料
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="label">用戶名</label>
              <input
                type="text"
                value={user?.username || ''}
                disabled
                className="input bg-gray-100 dark:bg-gray-700 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="label">郵箱</label>
              <input
                type="email"
                value={user?.email || ''}
                disabled
                className="input bg-gray-100 dark:bg-gray-700 cursor-not-allowed"
              />
            </div>
            <div>
              <label className="label">姓名</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label">公司名稱</label>
              <input
                type="text"
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                className="input"
              />
            </div>
          </div>
        </div>

        {/* Email Settings */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Mail className="w-5 h-5 text-gray-400 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              郵件設置
            </h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="label">SendGrid API Key</label>
              <input
                type="password"
                placeholder="SG.xxxxxxxxxxxxxx"
                value={formData.sendgrid_api_key}
                onChange={(e) => setFormData({ ...formData, sendgrid_api_key: e.target.value })}
                className="input"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                從 SendGrid 控制台獲取您的 API Key
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="label">發件人郵箱</label>
                <input
                  type="email"
                  placeholder="noreply@yourdomain.com"
                  value={formData.email_from_address}
                  onChange={(e) => setFormData({ ...formData, email_from_address: e.target.value })}
                  className="input"
                />
              </div>
              <div>
                <label className="label">發件人名稱</label>
                <input
                  type="text"
                  placeholder="Your Company"
                  value={formData.email_from_name}
                  onChange={(e) => setFormData({ ...formData, email_from_name: e.target.value })}
                  className="input"
                />
              </div>
            </div>
          </div>
        </div>

        {/* API Keys */}
        <div className="card">
          <div className="flex items-center mb-4">
            <Key className="w-5 h-5 text-gray-400 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              API 配置
            </h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="label">OpenAI API Key</label>
              <input
                type="password"
                placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
                className="input"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                用於 AI 郵件生成和優化
              </p>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center"
          >
            <Save className="w-4 h-4 mr-2" />
            {loading ? '保存中...' : '保存設置'}
          </button>
        </div>
      </form>
    </div>
  )
}
