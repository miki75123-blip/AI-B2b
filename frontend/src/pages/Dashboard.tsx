import { useQuery } from '@tanstack/react-query'
import { api } from '../services/api'
import {
  Users,
  Mail,
  Send,
  TrendingUp,
  TrendingDown,
  Eye,
  MousePointer,
  AlertCircle,
} from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface DashboardData {
  supplier_stats: {
    total: number
    verified: number
    pending: number
    contacted: number
    customers: number
  }
  email_stats: {
    total_sent: number
    total_opened: number
    total_clicked: number
    open_rate: number
    click_rate: number
  }
  campaign_stats: {
    total: number
    active: number
  }
  recent_activities: Array<{
    id: number
    activity_type: string
    title: string
    description: string
    success: boolean
    created_at: string
  }>
  top_campaigns: Array<{
    id: number
    name: string
    status: string
    emails_sent: number
    open_rate: number
    click_rate: number
  }>
}

export function Dashboard() {
  const { data: dashboard, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await api.get('/api/dashboard/')
      return response.data
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">儀表板</h1>
        <p className="text-gray-600 dark:text-gray-400">系統總覽和關鍵指標</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="總供應商"
          value={dashboard?.supplier_stats.total || 0}
          icon={Users}
          trend={12}
          trendUp={true}
        />
        <StatCard
          title="已驗證"
          value={dashboard?.supplier_stats.verified || 0}
          icon={Users}
          trend={8}
          trendUp={true}
        />
        <StatCard
          title="已發送郵件"
          value={dashboard?.email_stats.total_sent || 0}
          icon={Send}
          trend={dashboard?.email_stats.total_sent ? 15 : 0}
          trendUp={true}
        />
        <StatCard
          title="活動數量"
          value={dashboard?.campaign_stats.active || 0}
          icon={Mail}
          suffix=" / " + (dashboard?.campaign_stats.total || 0)
        />
      </div>

      {/* Email Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            郵件效能
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Eye className="w-5 h-5 text-primary-600 mr-2" />
                <span className="text-gray-600 dark:text-gray-400">打開率</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                {dashboard?.email_stats.open_rate || 0}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <MousePointer className="w-5 h-5 text-primary-600 mr-2" />
                <span className="text-gray-600 dark:text-gray-400">點擊率</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                {dashboard?.email_stats.click_rate || 0}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                <span className="text-gray-600 dark:text-gray-400">總打開數</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                {dashboard?.email_stats.total_opened || 0}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <TrendingUp className="w-5 h-5 text-green-600 mr-2" />
                <span className="text-gray-600 dark:text-gray-400">總點擊數</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                {dashboard?.email_stats.total_clicked || 0}
              </span>
            </div>
          </div>
        </div>

        {/* Top Campaigns */}
        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            表現最好的活動
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-sm text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                  <th className="pb-3 font-medium">活動名稱</th>
                  <th className="pb-3 font-medium">狀態</th>
                  <th className="pb-3 font-medium">已發送</th>
                  <th className="pb-3 font-medium">打開率</th>
                  <th className="pb-3 font-medium">點擊率</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {dashboard?.top_campaigns?.map((campaign) => (
                  <tr key={campaign.id}>
                    <td className="py-3 text-gray-900 dark:text-white">{campaign.name}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        campaign.status === 'running'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-400'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                      }`}>
                        {campaign.status}
                      </span>
                    </td>
                    <td className="py-3 text-gray-600 dark:text-gray-400">{campaign.emails_sent}</td>
                    <td className="py-3 text-gray-600 dark:text-gray-400">{campaign.open_rate}%</td>
                    <td className="py-3 text-gray-600 dark:text-gray-400">{campaign.click_rate}%</td>
                  </tr>
                ))}
                {(!dashboard?.top_campaigns || dashboard.top_campaigns.length === 0) && (
                  <tr>
                    <td colSpan={5} className="py-6 text-center text-gray-500 dark:text-gray-400">
                      暫無活動數據
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          最近活動
        </h3>
        <div className="space-y-3">
          {dashboard?.recent_activities?.slice(0, 5).map((activity) => (
            <div
              key={activity.id}
              className="flex items-start space-x-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50"
            >
              <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${
                activity.success ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {activity.title}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  {activity.description}
                </p>
              </div>
              <span className="text-xs text-gray-400 dark:text-gray-500">
                {new Date(activity.created_at).toLocaleString()}
              </span>
            </div>
          ))}
          {(!dashboard?.recent_activities || dashboard.recent_activities.length === 0) && (
            <p className="text-center text-gray-500 dark:text-gray-400 py-6">
              暫無活動記錄
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({
  title,
  value,
  icon: Icon,
  trend,
  trendUp,
  suffix,
}: {
  title: string
  value: number
  icon: any
  trend?: number
  trendUp?: boolean
  suffix?: string
}) {
  return (
    <div className="card">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="p-2 bg-primary-100 dark:bg-primary-900/50 rounded-lg">
            <Icon className="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
        </div>
        {trend !== undefined && (
          <div className={`flex items-center text-sm ${trendUp ? 'text-green-600' : 'text-red-600'}`}>
            {trendUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span className="ml-1">{trend}%</span>
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-3xl font-bold text-gray-900 dark:text-white">
          {value}{suffix}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400">{title}</p>
      </div>
    </div>
  )
}
