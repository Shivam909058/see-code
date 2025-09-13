import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api } from '@/lib/api'

interface User {
  id: string
  email: string
  github_username?: string
  created_at: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (token: string, user: User) => void
  logout: () => void
  checkAuth: () => Promise<void>
  githubLogin: () => Promise<void>
  handleGithubCallback: (code: string) => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      isAuthenticated: false,

      login: (token: string, user: User) => {
        set({ user, token, isAuthenticated: true })
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
        delete api.defaults.headers.common['Authorization']
        localStorage.removeItem('auth-storage')
      },

      checkAuth: async () => {
        const { token } = get()
        if (!token) {
          set({ isLoading: false })
          return
        }

        try {
          set({ isLoading: true })
          const response = await api.get('/auth/me')
          set({ 
            user: response.data, 
            isAuthenticated: true, 
            isLoading: false 
          })
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        } catch (error) {
          console.error('Auth check failed:', error)
          get().logout()
          set({ isLoading: false })
        }
      },

      githubLogin: async () => {
        try {
          // For Supabase OAuth, redirect directly to Supabase auth URL
          const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://qidfvvkrofeqtdjvzlqf.supabase.co'
          const redirectTo = encodeURIComponent(window.location.origin + '/auth/callback')
          
          const authUrl = `${supabaseUrl}/auth/v1/authorize?provider=github&redirect_to=${redirectTo}`
          
          window.location.href = authUrl
        } catch (error) {
          console.error('GitHub login failed:', error)
          throw error
        }
      },

      handleGithubCallback: async (code: string) => {
        try {
          set({ isLoading: true })
          const response = await api.post('/auth/github/callback', { code })
          
          const { access_token, user } = response.data
          get().login(access_token, user)
          
          // Redirect to dashboard
          window.location.href = '/dashboard'
        } catch (error) {
          console.error('GitHub callback failed:', error)
          set({ isLoading: false })
          throw error
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        token: state.token, 
        user: state.user,
        isAuthenticated: state.isAuthenticated
      }),
    }
  )
)