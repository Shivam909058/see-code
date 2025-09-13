import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner' 

export function AuthCallbackPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { handleGithubCallback } = useAuthStore()

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const error = searchParams.get('error')

      if (error) {
        console.error('OAuth error:', error)
        navigate('/?error=' + encodeURIComponent(error))
        return
      }

      if (code) {
        try {
          await handleGithubCallback(code)
          // Redirect will be handled by the callback function
        } catch (error) {
          console.error('Callback error:', error)
          navigate('/?error=' + encodeURIComponent('Authentication failed'))
        }
      } else {
        navigate('/')
      }
    }

    handleCallback()
  }, [searchParams, handleGithubCallback, navigate])

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner />
        <p className="mt-4 text-lg">Completing authentication...</p>
      </div>
    </div>
  )
}
