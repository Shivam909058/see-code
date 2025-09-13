import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface QualityOverviewProps {
  data: {
    quality_metrics?: {
      overall_score?: number
      security_score?: number
      performance_score?: number
      maintainability_score?: number
      documentation_coverage?: number
      test_coverage?: number
    }
    summary?: string
    issues?: Array<{
      category: string
      severity: string
    }>
    recommendations?: string[]
  }
}

export function QualityOverview({ data }: QualityOverviewProps) {
  const metrics = [
    {
      name: 'Overall Score',
      value: data.quality_metrics?.overall_score || 0,
      description: 'Overall code quality',
      trend: 'up' as const
    },
    {
      name: 'Security',
      value: data.quality_metrics?.security_score || 0,
      description: 'Security vulnerabilities',
      trend: 'up' as const
    },
    {
      name: 'Performance',
      value: data.quality_metrics?.performance_score || 0,
      description: 'Performance optimizations',
      trend: 'stable' as const
    },
    {
      name: 'Maintainability',
      value: data.quality_metrics?.maintainability_score || 0,
      description: 'Code maintainability',
      trend: 'up' as const
    }
  ]

  const getTrendIcon = (trend: 'up' | 'down' | 'stable') => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />
      case 'down':
        return <TrendingDown className="w-4 h-4 text-red-500" />
      default:
        return <Minus className="w-4 h-4 text-gray-500" />
    }
  }

  const issuesByCategory = (data.issues || []).reduce((acc, issue) => {
    acc[issue.category] = (acc[issue.category] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const issuesBySeverity = (data.issues || []).reduce((acc, issue) => {
    acc[issue.severity] = (acc[issue.severity] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="space-y-6">
      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Analysis Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground leading-relaxed">
            {data.summary || 'Comprehensive code quality analysis completed successfully.'}
          </p>
        </CardContent>
      </Card>

      {/* Quality Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-muted-foreground">
                    {metric.name}
                  </span>
                  {getTrendIcon(metric.trend)}
                </div>
                <div className="text-2xl font-bold mb-1">
                  {metric.value.toFixed(1)}%
                </div>
                <p className="text-xs text-muted-foreground">
                  {metric.description}
                </p>
                <div className="mt-3 w-full bg-muted rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(metric.value, 100)}%` }}
                  />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Issues Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Issues by Category */}
        <Card>
          <CardHeader>
            <CardTitle>Issues by Category</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(issuesByCategory).length > 0 ? (
                Object.entries(issuesByCategory).map(([category, count]) => (
                  <div key={category} className="flex items-center justify-between">
                    <span className="text-sm capitalize">{category}</span>
                    <Badge variant="outline">{count}</Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No issues found</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Issues by Severity */}
        <Card>
          <CardHeader>
            <CardTitle>Issues by Severity</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(issuesBySeverity).length > 0 ? (
                Object.entries(issuesBySeverity).map(([severity, count]) => (
                  <div key={severity} className="flex items-center justify-between">
                    <span className="text-sm capitalize">{severity}</span>
                    <Badge 
                      variant={
                        severity === 'critical' ? 'destructive' : 
                        severity === 'high' ? 'destructive' : 
                        'outline'
                      }
                    >
                      {count}
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">No issues found</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Key Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {data.recommendations.slice(0, 5).map((recommendation, index) => (
                <li key={index} className="text-sm text-muted-foreground flex items-start">
                  <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                  {recommendation}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}