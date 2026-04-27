import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { api } from '../services/api'
import toast from 'react-hot-toast'

interface User {
  id: number
  email: string
  username: string
  full_name?: string
  company_name?: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
}

interface RegisterData {
  email: string
  username: string
  password: string
  full_name?: string
  company_name?: string
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      
      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      await fetchUser()
      toast.success('登入成功！')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '登入失敗')
      throw error
    }
  }

  const register = async (data: RegisterData) => {
    try {
      await api.post('/api/auth/register', data)
      toast.success('註冊成功！請登入')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '註冊失敗')
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
    toast.success('已登出')
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
