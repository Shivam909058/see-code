import { motion } from 'framer-motion'
import { Zap, TrendingUp, Clock, Database } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { getSeverityColor } from '@/lib/utils'

interface PerformanceIssue {
  id: string
  severity: string
  title: string
  description: string
  file_path: string
  line_number?: number
  suggestion: string
  impact_score: number
  confidence: number
}

interface PerformanceReportProps {
  issues: PerformanceIssue[]
}

export function PerformanceReport({ issues }: PerformanceReportProps) {
  const categories = {
    'Database': issues.filter(i => i.title.toLowerCase().includes('database') || i.title.toLowerCase().includes('query')),
    'Algorithms': issues.filter(i => i.title.toLowerCase().includes('loop') || i.title.toLowerCase().includes('complexity')),
    'I/O Operations': issues.filter(i => i.title.toLowerCase().includes('i/o') || i.title.toLowerCase().includes('file')),
    'Memory': issues.filter(i => i.title.toLowerCase().includes('memory') || i.title.toLowerCase().includes('leak'))
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Database':
        return <Database className="w-5 h-5" />
      case 'Algorithms':
        return <TrendingUp className="w-5 h-5" />
      case 'I/O Operations':
        return <Clock className="w-5 h-5" />
      default:
        return <Zap className="w-5 h-5" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Performance Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Zap className="w-6 h-6 mr-2" />
            Performance Analysis
          </CardTitle>
          <CardDescription>
            Identify bottlenecks and optimization opportunities
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(categories).map(([category, categoryIssues]) => (
              <div key={category} className="text-center">
                <div className="flex items-center justify-center mb-2 text-blue-500">
                  {getCategoryIcon(category)}
                </div>
                <div className="text-2xl font-bold">{categoryIssues.length}</div>
                <div className="text-sm text-muted-foreground">
                  {category}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Issues by Category */}
      {Object.entries(categories).map(([category, categoryIssues]) => (
        categoryIssues.length > 0 && (
          <Card key={category}>
            <CardHeader>
              <CardTitle className="flex items-center">
                {getCategoryIcon(category)}
                <span className="ml-2">{category} Issues</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {categoryIssues.map((issue, index) => (
                  <motion.div
                    key={issue.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border rounded-lg p-4"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <Badge variant={getSeverityColor(issue.severity) as any}>
                        {issue.severity.toUpperCase()}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        Impact: {issue.impact_score.toFixed(1)}/10
                      </span>
                    </div>
                    
                    <h3 className="font-semibold mb-2">{issue.title}</h3>
                    <p className="text-sm text-muted-foreground mb-3">
                      {issue.description}
                    </p>
                    
                    <div className="text-xs text-muted-foreground mb-3">
                      <span className="font-medium">Location:</span> {issue.file_path}
                      {issue.line_number && ` (Line ${issue.line_number})`}
                    </div>
                    
                    <div className="bg-green-50 dark:bg-green-950/20 rounded-md p-3">
                      <p className="text-sm">
                        <span className="font-medium text-green-700 dark:text-green-300">
                          🚀 Optimization:
                        </span>{' '}
                        {issue.suggestion}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        )
      ))}

      {issues.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Zap className="w-12 h-12 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-green-700 dark:text-green-300 mb-2">
              Great Performance!
            </h3>
            <p className="text-muted-foreground">
              No significant performance issues detected in your code.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

