import { api } from './api'

export interface Campaign {
  id: number
  owner_id: number
  name: string
  description?: string
  target_countries?: string[]
  target_business_types?: string[]
  target_product_categories?: string[]
  email_template_id?: number
  daily_send_limit: number
  total_send_limit: number
  emails_sent: number
  emails_opened: number
  emails_clicked: number
  emails_bounced: number
  unsubscribes: number
  status: string
  open_rate: number
  click_rate: number
  created_at: string
  updated_at: string
}

export interface CreateCampaignData {
  name: string
  description?: string
  target_countries?: string[]
  target_business_types?: string[]
  email_template_id?: number
  daily_send_limit?: number
  total_send_limit?: number
}

export const campaignsApi = {
  list: async (params?: {
    skip?: number
    limit?: number
    status?: string
  }): Promise<Campaign[]> => {
    const response = await api.get('/api/campaigns/', { params })
    return response.data
  },

  get: async (id: number): Promise<Campaign> => {
    const response = await api.get(`/api/campaigns/${id}`)
    return response.data
  },

  create: async (data: CreateCampaignData): Promise<Campaign> => {
    const response = await api.post('/api/campaigns/', data)
    return response.data
  },

  update: async (id: number, data: Partial<CreateCampaignData>): Promise<Campaign> => {
    const response = await api.put(`/api/campaigns/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/campaigns/${id}`)
  },

  start: async (id: number): Promise<void> => {
    await api.post(`/api/campaigns/${id}/start`)
  },

  pause: async (id: number): Promise<void> => {
    await api.post(`/api/campaigns/${id}/pause`)
  },

  stop: async (id: number): Promise<void> => {
    await api.post(`/api/campaigns/${id}/stop`)
  },

  getStats: async () => {
    const response = await api.get('/api/campaigns/stats')
    return response.data
  },
}
