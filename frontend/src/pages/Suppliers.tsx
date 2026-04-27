import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { suppliersApi, Supplier, CreateSupplierData } from '../services/suppliers'
import toast from 'react-hot-toast'
import { Plus, Search, RefreshCw, MoreVertical, Trash2, Ban } from 'lucide-react'

export function Suppliers() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingSupplier, setEditingSupplier] = useState<Supplier | null>(null)

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['suppliers', page, search],
    queryFn: () => suppliersApi.list({ page, page_size: 20, search }),
  })

  const createMutation = useMutation({
    mutationFn: (data: CreateSupplierData) => suppliersApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
      toast.success('供應商已創建')
      setShowModal(false)
    },
    onError: () => {
      toast.error('創建失敗')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => suppliersApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
      toast.success('供應商已刪除')
    },
  })

  const blacklistMutation = useMutation({
    mutationFn: (id: number) => suppliersApi.toggleBlacklist(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['suppliers'] })
      toast.success('已更新黑名單狀態')
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">供應商管理</h1>
          <p className="text-gray-600 dark:text-gray-400">管理您的 B2B 潛在客戶</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => refetch()}
            className="btn-secondary flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            刷新
          </button>
          <button
            onClick={() => {
              setEditingSupplier(null)
              setShowModal(true)
            }}
            className="btn-primary flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            新增供應商
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="搜索供應商名稱、郵箱..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                <th className="pb-3 font-medium">公司名稱</th>
                <th className="pb-3 font-medium">國家</th>
                <th className="pb-3 font-medium">郵箱</th>
                <th className="pb-3 font-medium">驗證狀態</th>
                <th className="pb-3 font-medium">質量分數</th>
                <th className="pb-3 font-medium">已聯繫</th>
                <th className="pb-3 font-medium">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center">
                    <div className="flex justify-center">
                      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-600"></div>
                    </div>
                  </td>
                </tr>
              ) : data?.items?.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-gray-500 dark:text-gray-400">
                    暫無供應商數據
                  </td>
                </tr>
              ) : (
                data?.items?.map((supplier) => (
                  <tr key={supplier.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="py-3">
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {supplier.company_name}
                        </p>
                        {supplier.business_type && (
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {supplier.business_type}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="py-3 text-gray-600 dark:text-gray-400">
                      {supplier.country || '-'}
                    </td>
                    <td className="py-3 text-gray-600 dark:text-gray-400">
                      {supplier.email || '-'}
                    </td>
                    <td className="py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        supplier.verification_status === 'verified'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-400'
                          : supplier.verification_status === 'pending'
                          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-400'
                          : 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-400'
                      }`}>
                        {supplier.verification_status}
                      </span>
                    </td>
                    <td className="py-3">
                      <div className="flex items-center">
                        <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full mr-2">
                          <div
                            className={`h-2 rounded-full ${
                              supplier.quality_score >= 70
                                ? 'bg-green-500'
                                : supplier.quality_score >= 40
                                ? 'bg-yellow-500'
                                : 'bg-red-500'
                            }`}
                            style={{ width: `${supplier.quality_score}%` }}
                          />
                        </div>
                        <span className="text-sm text-gray-600 dark:text-gray-400">
                          {supplier.quality_score}
                        </span>
                      </div>
                    </td>
                    <td className="py-3">
                      {supplier.is_contacted ? (
                        <span className="text-primary-600 dark:text-primary-400">是</span>
                      ) : (
                        <span className="text-gray-400">否</span>
                      )}
                    </td>
                    <td className="py-3">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => blacklistMutation.mutate(supplier.id)}
                          className={`p-1 rounded ${
                            supplier.is_blacklisted
                              ? 'text-red-600 hover:bg-red-100 dark:hover:bg-red-900/50'
                              : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
                          }`}
                          title={supplier.is_blacklisted ? '移出黑名單' : '加入黑名單'}
                        >
                          <Ban className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => deleteMutation.mutate(supplier.id)}
                          className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                          title="刪除"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {data && data.total_pages > 1 && (
          <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              顯示 {(page - 1) * 20 + 1} - {Math.min(page * 20, data.total)} / 共 {data.total} 條
            </p>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50"
              >
                上一頁
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page === data.total_pages}
                className="btn-secondary disabled:opacity-50"
              >
                下一頁
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <SupplierModal
          supplier={editingSupplier}
          onClose={() => setShowModal(false)}
          onSubmit={(data) => createMutation.mutate(data)}
          isLoading={createMutation.isPending}
        />
      )}
    </div>
  )
}

function SupplierModal({
  supplier,
  onClose,
  onSubmit,
  isLoading,
}: {
  supplier: Supplier | null
  onClose: () => void
  onSubmit: (data: CreateSupplierData) => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState<CreateSupplierData>({
    company_name: supplier?.company_name || '',
    website: supplier?.website || '',
    email: supplier?.email || '',
    phone: supplier?.phone || '',
    country: supplier?.country || '',
    business_type: supplier?.business_type || '',
    description: supplier?.description || '',
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
            {supplier ? '編輯供應商' : '新增供應商'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label">公司名稱 *</label>
              <input
                type="text"
                required
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                className="input"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">郵箱</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="input"
                />
              </div>
              <div>
                <label className="label">電話</label>
                <input
                  type="text"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="input"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">國家</label>
                <input
                  type="text"
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  className="input"
                />
              </div>
              <div>
                <label className="label">企業類型</label>
                <input
                  type="text"
                  value={formData.business_type}
                  onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
                  className="input"
                />
              </div>
            </div>
            <div>
              <label className="label">網站</label>
              <input
                type="url"
                value={formData.website}
                onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                className="input"
                placeholder="https://"
              />
            </div>
            <div>
              <label className="label">描述</label>
              <textarea
                rows={3}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input"
              />
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
