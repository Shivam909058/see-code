import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  FileText, 
  Calendar, 
  Clock, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Eye, 
  Trash2, 
  RefreshCw,
  Github,
  Upload
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { analysisApi } from '@/lib/api'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

interface Analysis {
  id: string
  name: string
  type: 'github' | 'upload'
  status: 'pending' | 'processing' | 'completed' | 'failed'
  created_at: string
  repository_url?: string
  repository_info?: {
    path?: string
    file_names?: string[]
  }
  issues_count?: number
  processing_time?: number
  files_analyzed?: number
  lines_analyzed?: number
}

export function AnalysisHistory() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const { data: analysesData, isLoading, error, refetch } = useQuery({
    queryKey: ['analyses'],
    queryFn: async () => {
      const response = await analysisApi.getUserAnalyses(20) // Get last 20 analyses
      return response.data
    },
    refetchInterval: 5000, // Refresh every 5 seconds to show status updates
  })

  const deleteMutation = useMutation({
    mutationFn: async (analysisId: string) => {
      setDeletingId(analysisId)
      await analysisApi.deleteAnalysis(analysisId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analyses'] })
      toast.success('Analysis deleted successfully')
    },
    onError: (error) => {
      toast.error('Failed to delete analysis')
      console.error('Delete error:', error)
    },
    onSettled: () => {
      setDeletingId(null)
    }
  })

  const analyses = analysesData?.analyses || []

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-500'
      case 'processing': return 'text-blue-500'
      case 'pending': return 'text-yellow-500'
      case 'failed': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4" />
      case 'processing': return <RefreshCw className="w-4 h-4 animate-spin" />
      case 'pending': return <Clock className="w-4 h-4" />
      case 'failed': return <XCircle className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  const getTypeIcon = (type: string) => {
    return type === 'github' ? <Github className="w-4 h-4" /> : <Upload className="w-4 h-4" />
  }

  if (isLoading) {
    return (
      <Card className="max-w-4xl mx-auto">
        <CardContent className="flex items-center justify-center p-8">
          <LoadingSpinner size="lg" />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="max-w-4xl mx-auto">
        <CardContent className="text-center p-8">
          <p className="text-destructive mb-4">Failed to load analysis history</p>
          <Button onClick={() => refetch()}>Try Again</Button>
        </CardContent>
      </Card>
    )
  }

  if (analyses.length === 0) {
    return (
      <Card className="max-w-4xl mx-auto">
        <CardContent className="text-center p-8">
          <FileText className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">No Analysis History</h3>
          <p className="text-muted-foreground mb-4">
            You haven't run any code analyses yet. Start by uploading files or connecting a repository.
          </p>
          <Button onClick={() => navigate('/dashboard')}>
            Start Analysis
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Analysis History</h2>
          <p className="text-muted-foreground">View and manage your previous code analyses</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <AnimatePresence>
        {analyses.map((analysis: Analysis, index: number) => (
          <motion.div
            key={analysis.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getTypeIcon(analysis.type)}
                    <div>
                      <CardTitle className="text-lg">{analysis.name}</CardTitle>
                      <CardDescription className="flex items-center space-x-2 mt-1">
                        <Calendar className="w-3 h-3" />
                        <span>{new Date(analysis.created_at).toLocaleString()}</span>
                      </CardDescription>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <div className={`flex items-center space-x-1 ${getStatusColor(analysis.status)}`}>
                      {getStatusIcon(analysis.status)}
                      <span className="text-sm font-medium capitalize">{analysis.status}</span>
                    </div>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">
                      {analysis.files_analyzed || 0} files
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">
                      {analysis.issues_count || 0} issues
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Clock className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">
                      {analysis.processing_time ? `${analysis.processing_time.toFixed(1)}s` : 'N/A'}
                    </span>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline" className="text-xs">
                      {analysis.type === 'github' ? 'Repository' : 'Upload'}
                    </Badge>
                  </div>
                </div>
                
                {analysis.repository_info?.path && (
                  <div className="mb-4 p-2 bg-muted/50 rounded-md">
                    <p className="text-sm text-muted-foreground truncate">
                      {analysis.repository_info.path}
                    </p>
                  </div>
                )}
                
                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    {analysis.status === 'completed' && (
                      <Button
                        size="sm"
                        onClick={() => navigate(`/analysis/${analysis.id}`)}
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        View Results
                      </Button>
                    )}
                    
                    {analysis.status === 'processing' && (
                      <Button size="sm" variant="outline" disabled>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </Button>
                    )}
                    
                    {analysis.status === 'failed' && (
                      <Button size="sm" variant="outline" disabled>
                        <XCircle className="w-4 h-4 mr-2" />
                        Failed
                      </Button>
                    )}
                  </div>
                  
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => deleteMutation.mutate(analysis.id)}
                    disabled={deletingId === analysis.id}
                    className="text-destructive hover:text-destructive"
                  >
                    {deletingId === analysis.id ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}

