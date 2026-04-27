import { api } from './api'

export interface Supplier {
  id: number
  owner_id: number
  company_name: string
  website?: string
  email?: string
  phone?: string
  address?: string
  country?: string
  city?: string
  business_type?: string
  product_categories?: string[]
  description?: string
  source_platform: string
  verification_status: string
  quality_score: number
  is_contacted: boolean
  is_customer: boolean
  is_blacklisted: boolean
  created_at: string
  updated_at: string
}

export interface SupplierList {
  items: Supplier[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface CreateSupplierData {
  company_name: string
  website?: string
  email?: string
  phone?: string
  country?: string
  business_type?: string
  product_categories?: string[]
  description?: string
}

export const suppliersApi = {
  list: async (params?: {
    page?: number
    page_size?: number
    search?: string
    country?: string
    verification_status?: string
  }): Promise<SupplierList> => {
    const response = await api.get('/api/suppliers/', { params })
    return response.data
  },

  get: async (id: number): Promise<Supplier> => {
    const response = await api.get(`/api/suppliers/${id}`)
    return response.data
  },

  create: async (data: CreateSupplierData): Promise<Supplier> => {
    const response = await api.post('/api/suppliers/', data)
    return response.data
  },

  update: async (id: number, data: Partial<CreateSupplierData>): Promise<Supplier> => {
    const response = await api.put(`/api/suppliers/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/api/suppliers/${id}`)
  },

  scrape: async (platform: string, url?: string): Promise<{ task_id: string }> => {
    const response = await api.post('/api/suppliers/scrape', null, {
      params: { platform, url }
    })
    return response.data
  },

  toggleBlacklist: async (id: number): Promise<Supplier> => {
    const response = await api.post(`/api/suppliers/${id}/blacklist`)
    return response.data
  },
}
