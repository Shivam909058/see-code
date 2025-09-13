import axios from 'axios'
import toast from 'react-hot-toast'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth-storage')
    if (token) {
      try {
        const parsed = JSON.parse(token)
        if (parsed.state?.token) {
          config.headers.Authorization = `Bearer ${parsed.state.token}`
        }
      } catch (error) {
        console.error('Failed to parse auth token:', error)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('auth-storage')
      window.location.href = '/auth/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  githubLogin: () => api.get('/auth/oauth/github'),
  
  verifySupabaseToken: (token: string) =>
    api.post('/auth/verify-token', { token }),
  
  getCurrentUser: () => api.get('/auth/me'),
  
  logout: () => api.post('/auth/logout')
}

// Analysis API - Fixed endpoints
export const analysisApi = {
  // FIXED: Send repo_url instead of repository_url to match AnalysisRequest model
  analyzeRepository: (repoUrl: string, branch: string = 'main') =>
    api.post('/analyze/github', { 
      repo_url: repoUrl,  // FIXED: Use repo_url instead of repository_url
      branch: branch,
      name: `GitHub Analysis - ${repoUrl.split('/').pop()} - ${new Date().toLocaleDateString()}`
    }),
  
  // Fixed: Use /analyze instead of /api/analyze  
  analyzeFiles: (files: File[], name: string) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    formData.append('name', name)
    return api.post('/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // This one is correct - /api/qa exists
  askQuestion: (question: string, analysisId?: string, context?: string) =>
    api.post('/api/qa', { question, analysis_id: analysisId, context }),
  
  getAnalysis: (id: string) => api.get(`/analysis/${id}`),
  
  getUserAnalyses: (limit = 10) => api.get(`/analyses?limit=${limit}`),
  
  deleteAnalysis: (id: string) => api.delete(`/analysis/${id}`),
  
  // Fixed: Use /chat/{analysis_id} for chat
  chatAboutAnalysis: (analysisId: string, question: string) =>
    api.post(`/chat/${analysisId}`, new URLSearchParams({ question }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
}

// System API
export const systemApi = {
  getSupportedLanguages: () => api.get('/api/supported-languages'),
  getHealth: () => api.get('/api/health')
}

export default api