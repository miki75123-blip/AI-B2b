import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { campaignsApi, Campaign, CreateCampaignData } from '../services/campaigns'
import toast from 'react-hot-toast'
import { Plus, Play, Pause, Square, RefreshCw, Trash2 } from 'lucide-react'

export function Campaigns() {
  const queryClient = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null)

  const { data: campaigns, isLoading, refetch } = useQuery({
    queryKey: ['campaigns'],
    queryFn: () => campaignsApi.list(),
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateCampaignData) => campaignsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('活動已創建')
      setShowModal(false)
    },
    onError: () => {
      toast.error('創建失敗')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => campaignsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('活動已刪除')
    },
  })

  const startMutation = useMutation({
    mutationFn: (id: number) => campaignsApi.start(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('活動已啟動')
    },
  })

  const pauseMutation = useMutation({
    mutationFn: (id: number) => campaignsApi.pause(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('活動已暫停')
    },
  })

  const stopMutation = useMutation({
    mutationFn: (id: number) => campaignsApi.stop(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] })
      toast.success('活動已停止')
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">營銷活動</h1>
          <p className="text-gray-600 dark:text-gray-400">創建和管理您的郵件營銷活動</p>
        </div>
        <div className="flex space-x-3">
          <button onClick={() => refetch()} className="btn-secondary flex items-center">
            <RefreshCw className="w-4 h-4 mr-2" />
            刷新
          </button>
          <button
            onClick={() => {
              setEditingCampaign(null)
              setShowModal(true)
            }}
            className="btn-primary flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            新建活動
          </button>
        </div>
      </div>

      {/* Campaigns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
            </div>
          ))
        ) : campaigns?.length === 0 ? (
          <div className="col-span-full card text-center py-12">
            <p className="text-gray-500 dark:text-gray-400 mb-4">還沒有任何活動</p>
            <button
              onClick={() => setShowModal(true)}
              className="btn-primary"
            >
              創建您的第一個活動
            </button>
          </div>
        ) : (
          campaigns?.map((campaign) => (
            <div key={campaign.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    {campaign.name}
                  </h3>
                  <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full mt-2 ${
                    campaign.status === 'running'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-400'
                      : campaign.status === 'paused'
                      ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-400'
                      : campaign.status === 'completed'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-400'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-400'
                  }`}>
                    {campaign.status}
                  </span>
                </div>
                <div className="flex space-x-1">
                  {campaign.status === 'draft' || campaign.status === 'paused' ? (
                    <button
                      onClick={() => startMutation.mutate(campaign.id)}
                      className="p-2 text-green-600 hover:bg-green-100 dark:hover:bg-green-900/50 rounded"
                      title="啟動"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  ) : campaign.status === 'running' ? (
                    <>
                      <button
                        onClick={() => pauseMutation.mutate(campaign.id)}
                        className="p-2 text-yellow-600 hover:bg-yellow-100 dark:hover:bg-yellow-900/50 rounded"
                        title="暫停"
                      >
                        <Pause className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => stopMutation.mutate(campaign.id)}
                        className="p-2 text-red-600 hover:bg-red-100 dark:hover:bg-red-900/50 rounded"
                        title="停止"
                      >
                        <Square className="w-4 h-4" />
                      </button>
                    </>
                  ) : null}
                  <button
                    onClick={() => deleteMutation.mutate(campaign.id)}
                    className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 rounded"
                    title="刪除"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {campaign.description && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  {campaign.description}
                </p>
              )}

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">已發送</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {campaign.emails_sent} / {campaign.total_send_limit}
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full">
                  <div
                    className="h-2 bg-primary-600 rounded-full transition-all"
                    style={{ width: `${(campaign.emails_sent / campaign.total_send_limit) * 100}%` }}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">打開率</p>
                    <p className="text-lg font-bold text-primary-600">{campaign.open_rate}%</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 dark:text-gray-400">點擊率</p>
                    <p className="text-lg font-bold text-green-600">{campaign.click_rate}%</p>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <CampaignModal
          campaign={editingCampaign}
          onClose={() => setShowModal(false)}
          onSubmit={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
        />
      )}
    </div>
  )
}

function CampaignModal({
  campaign,
  onClose,
  onSubmit,
  isLoading,
}: {
  campaign: Campaign | null
  onClose: () => void
  onSubmit: (data: CreateCampaignData) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState<CreateCampaignData>({
    name: campaign?.name || '',
    description: campaign?.description || '',
    target_countries: campaign?.target_countries || [],
    daily_send_limit: campaign?.daily_send_limit || 50,
    total_send_limit: campaign?.total_send_limit || 1000,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-gray-900/50" onClick={onClose} />
        <div className="relative bg-white dark:bg-gray-800 rounded-lg w-full max-w-lg p-6 shadow-xl">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            {campaign ? '編輯活動' : '新建活動'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">活動名稱 *</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label">描述</label>
              <textarea
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input"
              />
            </div>
            <div>
              <label className="label">目標國家（逗號分隔）</label>
              <input
                type="text"
                placeholder="UK, USA, China"
                value={formData.target_countries?.join(', ') || ''}
                onChange={(e) => setFormData({
                  ...formData,
                  target_countries: e.target.value.split(',').map(s => s.trim()).filter(Boolean)
                })}
                className="input"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">每日發送上限</label>
                <input
                  type="number"
                  min={1}
                  value={formData.daily_send_limit}
                  onChange={(e) => setFormData({ ...formData, daily_send_limit: parseInt(e.target.value) })}
                  className="input"
                />
              </div>
              <div>
                <label className="label">總發送上限</label>
                <input
                  type="number"
                  min={1}
                  value={formData.total_send_limit}
                  onChange={(e) => setFormData({ ...formData, total_send_limit: parseInt(e.target.value) })}
                  className="input"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-3 pt-4">
              <button type="button" onClick={onClose} className="btn-secondary">
                取消
              </button>
              <button type="submit" disabled={isLoading} className="btn-primary disabled:opacity-50">
                {isLoading ? '保存中...' : '保存'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
