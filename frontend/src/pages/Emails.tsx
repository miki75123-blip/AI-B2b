import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import { Eye, MousePointer, Mail, Send } from 'lucide-react'

interface EmailTemplate {
  id: number
  name: string
  description?: string
  subject_template: string
  body_template: string
  is_active: boolean
  is_default: boolean
  usage_count: number
  created_at: string
}

export function Emails() {
  const { data: templates, isLoading } = useQuery<EmailTemplate[]>({
    queryKey: ['email-templates'],
    queryFn: async () => {
      const response = await api.get('/api/emails/templates')
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">郵件管理</h1>
          <p className="text-gray-600 dark:text-gray-400">管理您的郵件模板</p>
        </div>
        <button className="btn-primary flex items-center">
          <Mail className="w-4 h-4 mr-2" />
          新建模板
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/50 rounded-lg">
              <Mail className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {templates?.length || 0}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">總模板數</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 dark:bg-green-900/50 rounded-lg">
              <Send className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {templates?.filter(t => t.is_default).length || 0}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">默認模板</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/50 rounded-lg">
              <MousePointer className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div className="ml-4">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {templates?.reduce((acc, t) => acc + t.usage_count, 0) || 0}
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">總使用次數</p>
            </div>
          </div>
        </div>
      </div>

      {/* Templates */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          郵件模板
        </h3>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
          </div>
        ) : templates?.length === 0 ? (
          <div className="text-center py-8">
            <Mail className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400 mb-4">還沒有任何模板</p>
            <button className="btn-primary">創建您的第一個模板</button>
          </div>
        ) : (
          <div className="space-y-4">
            {templates?.map((template) => (
              <div
                key={template.id}
                className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        {template.name}
                      </h4>
                      {template.is_default && (
                        <span className="ml-2 px-2 py-0.5 text-xs bg-primary-100 text-primary-800 dark:bg-primary-900/50 dark:text-primary-400 rounded">
                          默認
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      主題：{template.subject_template}
                    </p>
                    {template.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-2 line-clamp-2">
                        {template.description}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                      <Eye className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                      <MousePointer className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    使用次數：{template.usage_count}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(template.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
