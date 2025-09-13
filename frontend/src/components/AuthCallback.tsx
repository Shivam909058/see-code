import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/lib/api'
import { LoadingSpinner } from './ui/LoadingSpinner'
import toast from 'react-hot-toast'

export function AuthCallback() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { login } = useAuthStore()
  const [isProcessing, setIsProcessing] = useState(true)

  useEffect(() => {
    const handleCallback = async () => {
      try {
        setIsProcessing(true)

        // Check for errors first
        const error = searchParams.get('error')
        const errorDescription = searchParams.get('error_description')
        
        if (error) {
          console.error('OAuth error:', error, errorDescription)
          toast.error(`Authentication failed: ${errorDescription || error}`)
          navigate('/')
          return
        }

        // Method 1: Check for direct authorization code (GitHub OAuth)
        const code = searchParams.get('code')
        const state = searchParams.get('state')

        if (code) {
          console.log('Processing GitHub OAuth code:', code)
          try {
            const response = await authApi.githubCallback(code, state || undefined)
            const { access_token, user } = response.data

            login(access_token, user)
            toast.success('Successfully logged in!')
            navigate('/dashboard')
            return
          } catch (error) {
            console.error('GitHub OAuth callback error:', error)
            toast.error('GitHub authentication failed')
            navigate('/')
            return
          }
        }

        // Method 2: Check for Supabase OAuth tokens in URL fragment
        const fragment = window.location.hash.substring(1)
        const fragmentParams = new URLSearchParams(fragment)
        
        const accessToken = fragmentParams.get('access_token')
        const refreshToken = fragmentParams.get('refresh_token')
        const tokenType = fragmentParams.get('token_type')

        if (accessToken) {
          console.log('Processing Supabase OAuth token')
          try {
            // Verify the token with our backend
            const response = await authApi.verifySupabaseToken(accessToken)
            const { user } = response.data

            login(accessToken, user)
            toast.success('Successfully logged in!')
            navigate('/dashboard')
            return
          } catch (error) {
            console.error('Supabase token verification error:', error)
            toast.error('Token verification failed')
            navigate('/')
            return
          }
        }

        // Method 3: Check for Supabase session in URL
        const sessionParam = searchParams.get('session')
        if (sessionParam) {
          console.log('Processing Supabase session')
          try {
            const sessionData = JSON.parse(decodeURIComponent(sessionParam))
            if (sessionData.access_token) {
              const response = await authApi.verifySupabaseToken(sessionData.access_token)
              const { user } = response.data

              login(sessionData.access_token, user)
              toast.success('Successfully logged in!')
              navigate('/dashboard')
              return
            }
          } catch (error) {
            console.error('Session parsing error:', error)
          }
        }

        // If we get here, no valid auth data was found
        console.warn('No authorization code, token, or session found in callback')
        console.log('Search params:', Object.fromEntries(searchParams.entries()))
        console.log('URL fragment:', fragment)
        console.log('Full URL:', window.location.href)
        
        toast.error('No authorization data received. Please try logging in again.')
        navigate('/')

      } catch (error) {
        console.error('Auth callback error:', error)
        toast.error('Authentication failed')
        navigate('/')
      } finally {
        setIsProcessing(false)
      }
    }

    // Small delay to ensure URL is fully loaded
    const timer = setTimeout(handleCallback, 100)
    return () => clearTimeout(timer)
  }, [searchParams, navigate, login])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <p className="mt-4 text-muted-foreground">
          {isProcessing ? 'Completing authentication...' : 'Processing login...'}
        </p>
      </div>
    </div>
  )
}