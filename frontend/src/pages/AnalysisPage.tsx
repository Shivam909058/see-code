import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, 
  Download, 
  MessageSquare,
  BarChart3,
  Shield,
  Zap,
  Brain,
  RefreshCw
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Badge } from '@/components/ui/Badge'
import { QualityOverview } from '@/components/analysis/QualityOverview'
import { IssuesTable } from '@/components/analysis/IssuesTable'
import { LanguageStats } from '@/components/analysis/LanguageStats'
import { SecurityReport } from '@/components/analysis/SecurityReport'
import { PerformanceReport } from '@/components/analysis/PerformanceReport'
import { ComplexityReport } from '@/components/analysis/ComplexityReport'
import { InteractiveQA } from '@/components/InteractiveQA'
import { analysisApi } from '@/lib/api'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import toast from 'react-hot-toast'

interface AnalysisData {
  id: string
  name: string
  type: string
  status: string
  created_at: string
  repository_info: {
    path?: string
    file_names?: string[]
    total_files?: number
    total_lines?: number
  }
  quality_metrics: {
    overall_score: number
    security_score: number
    performance_score: number
    maintainability_score: number
    documentation_coverage: number
    test_coverage: number
  }
  language_stats: Array<{
    language: string
    files_count: number
    lines_of_code: number
    percentage: number
    complexity_score: number
  }>
  issues: Array<{
    id: string
    category: string
    severity: string
    title: string
    description: string
    file_path: string
    line_number?: number
    suggestion: string
    impact_score: number
    confidence: number
  }>
  summary: string
  recommendations: string[]
  architecture_insights: Array<{
    type: string
    description: string
    impact: string
    recommendations: string[]
  }>
  dependencies: Array<{
    name: string
    version: string
    vulnerabilities: number
    outdated: boolean
  }>
  processing_time: number
  files_analyzed: number
  lines_analyzed: number
  issues_count: number
}

export function AnalysisPage() {
  const { analysisId } = useParams<{ analysisId: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'overview' | 'issues' | 'security' | 'performance' | 'complexity' | 'qa'>('overview')
  const [isExporting, setIsExporting] = useState(false)

  const { data: analysisData, isLoading, error, refetch } = useQuery({
    queryKey: ['analysis', analysisId],
    queryFn: async (): Promise<AnalysisData> => {
      if (!analysisId) throw new Error('Analysis ID is required')
      
      const response = await analysisApi.getAnalysis(analysisId)
      return response.data
    },
    enabled: !!analysisId,
    retry: 3,
    refetchInterval: (data) => {
      // If analysis is still processing, refetch every 3 seconds
      if (data?.status === 'processing' || data?.status === 'pending') {
        return 3000
      }
      return false
    }
  })

  const handleExport = async () => {
    if (!analysisData) return
    
    setIsExporting(true)
    try {
      // Create detailed report
      const report = generateDetailedReport(analysisData)
      
      // Create and download file
      const blob = new Blob([report], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `code-analysis-report-${analysisData.name}-${new Date().toISOString().split('T')[0]}.md`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      toast.success('Report exported successfully!')
    } catch (error) {
      toast.error('Failed to export report')
    } finally {
      setIsExporting(false)
    }
  }

  const generateDetailedReport = (data: AnalysisData): string => {
    return `# Code Quality Analysis Report

**Analysis Name:** ${data.name}
**Date:** ${new Date(data.created_at).toLocaleDateString()}
**Status:** ${data.status}
**Processing Time:** ${data.processing_time?.toFixed(2)}s

## Executive Summary

${data.summary || 'Comprehensive code quality analysis completed.'}

## Quality Metrics

- **Overall Score:** ${data.quality_metrics?.overall_score?.toFixed(1) || 'N/A'}/100
- **Security Score:** ${data.quality_metrics?.security_score?.toFixed(1) || 'N/A'}/100
- **Performance Score:** ${data.quality_metrics?.performance_score?.toFixed(1) || 'N/A'}/100
- **Maintainability Score:** ${data.quality_metrics?.maintainability_score?.toFixed(1) || 'N/A'}/100
- **Documentation Coverage:** ${data.quality_metrics?.documentation_coverage?.toFixed(1) || 'N/A'}%

## Repository Information

- **Path:** ${data.repository_info?.path || 'Local Files'}
- **Files Analyzed:** ${data.files_analyzed || 0}
- **Lines Analyzed:** ${data.lines_analyzed || 0}
- **Total Issues Found:** ${data.issues_count || data.issues?.length || 0}

## Issues Breakdown

${data.issues?.map(issue => `
### ${issue.title}

**Category:** ${issue.category}
**Severity:** ${issue.severity.toUpperCase()}
**File:** ${issue.file_path}${issue.line_number ? ` (Line ${issue.line_number})` : ''}
**Impact Score:** ${issue.impact_score}/10
**Confidence:** ${(issue.confidence * 100).toFixed(1)}%

**Description:**
${issue.description}

**Recommended Solution:**
${issue.suggestion}

---
`).join('') || 'No issues found.'}

## Architecture Insights

${data.architecture_insights?.map(insight => `
### ${insight.type}

**Description:** ${insight.description}
**Impact:** ${insight.impact}

**Recommendations:**
${insight.recommendations?.map(rec => `- ${rec}`).join('\n') || ''}

---
`).join('') || 'No architecture insights available.'}

## Recommendations

${data.recommendations?.map(rec => `- ${rec}`).join('\n') || 'No specific recommendations available.'}

## Language Statistics

${data.language_stats?.map(stat => `
- **${stat.language}:** ${stat.files_count} files, ${stat.lines_of_code} lines (${stat.percentage?.toFixed(1)}%)
`).join('') || 'No language statistics available.'}

---

*Generated by Code Quality Intelligence Agent*
*Report Date: ${new Date().toISOString()}*
`
  }

  const tabs = [
    { id: 'overview' as const, label: 'Overview', icon: BarChart3 },
    { id: 'issues' as const, label: 'Issues', icon: Shield },
    { id: 'security' as const, label: 'Security', icon: Shield },
    { id: 'performance' as const, label: 'Performance', icon: Zap },
    { id: 'complexity' as const, label: 'Complexity', icon: Brain },
    { id: 'qa' as const, label: 'Q&A', icon: MessageSquare }
  ]

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner className="w-8 h-8 mx-auto mb-4" />
          <p className="text-muted-foreground">Loading analysis results...</p>
          {analysisData?.status === 'processing' && (
            <p className="text-sm text-muted-foreground mt-2">Analysis in progress...</p>
          )}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">Failed to load analysis</p>
          <Button onClick={() => refetch()}>Try Again</Button>
        </div>
      </div>
    )
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground">No analysis data found</p>
          <Button onClick={() => navigate('/dashboard')} className="mt-4">
            Back to Dashboard
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate('/dashboard')}
                className="flex items-center space-x-2"
              >
                <ArrowLeft className="w-4 h-4" />
                <span>Back</span>
              </Button>
              
              <div>
                <h1 className="text-2xl font-bold">{analysisData.name}</h1>
                <p className="text-sm text-muted-foreground">
                  {analysisData.repository_info?.path || 'Local Files'} • 
                  {analysisData.files_analyzed || 0} files • 
                  {analysisData.lines_analyzed || 0} lines
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleExport}
                disabled={isExporting}
              >
                <Download className="w-4 h-4 mr-2" />
                {isExporting ? 'Exporting...' : 'Export Report'}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetch()}
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3 space-y-6">
            {/* Status Banner */}
            {analysisData.status === 'processing' && (
              <Card className="bg-blue-50 border-blue-200">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="w-4 h-4 animate-spin text-blue-500" />
                    <span className="text-blue-700">Analysis in progress...</span>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Tabs */}
            <div className="flex space-x-1 bg-muted/50 rounded-lg p-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'bg-background shadow-sm text-foreground'
                      : 'text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              {activeTab === 'overview' && <QualityOverview data={analysisData} />}
              {activeTab === 'issues' && <IssuesTable issues={analysisData.issues || []} />}
              {activeTab === 'security' && <SecurityReport issues={(analysisData.issues || []).filter(i => i.category === 'security')} />}
              {activeTab === 'performance' && <PerformanceReport issues={(analysisData.issues || []).filter(i => i.category === 'performance')} />}
              {activeTab === 'complexity' && <ComplexityReport data={analysisData} />}
              {activeTab === 'qa' && <InteractiveQA analysisId={analysisId!} />}
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Stats</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Total Issues</span>
                  <span className="font-medium">{analysisData.issues_count || analysisData.issues?.length || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Critical</span>
                  <span className="font-medium text-red-500">
                    {(analysisData.issues || []).filter(i => i.severity === 'critical').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">High</span>
                  <span className="font-medium text-orange-500">
                    {(analysisData.issues || []).filter(i => i.severity === 'high').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Processing Time</span>
                  <span className="font-medium">{analysisData.processing_time?.toFixed(1) || 0}s</span>
                </div>
              </CardContent>
            </Card>

            {/* Q&A Button */}
            <Card>
              <CardHeader>
                <CardTitle>Interactive Q&A</CardTitle>
                <CardDescription>
                  Ask questions about your codebase
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={() => setActiveTab('qa')} 
                  className="w-full"
                  variant={activeTab === 'qa' ? 'default' : 'outline'}
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Start Q&A Session
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}