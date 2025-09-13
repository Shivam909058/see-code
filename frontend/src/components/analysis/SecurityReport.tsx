import { motion } from 'framer-motion'
import { Shield, AlertTriangle, Info, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { getSeverityColor } from '@/lib/utils'

interface SecurityIssue {
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

interface SecurityReportProps {
  issues: SecurityIssue[]
}

export function SecurityReport({ issues }: SecurityReportProps) {
  const severityCounts = issues.reduce((acc, issue) => {
    acc[issue.severity] = (acc[issue.severity] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="w-5 h-5 text-red-500" />
      case 'medium':
        return <Info className="w-5 h-5 text-yellow-500" />
      default:
        return <CheckCircle className="w-5 h-5 text-green-500" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Security Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="w-6 h-6 mr-2" />
            Security Analysis
          </CardTitle>
          <CardDescription>
            Comprehensive security vulnerability assessment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(severityCounts).map(([severity, count]) => (
              <div key={severity} className="text-center">
                <div className="flex items-center justify-center mb-2">
                  {getSeverityIcon(severity)}
                </div>
                <div className="text-2xl font-bold">{count}</div>
                <div className="text-sm text-muted-foreground capitalize">
                  {severity} Issues
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Security Issues */}
      <Card>
        <CardHeader>
          <CardTitle>Security Vulnerabilities</CardTitle>
          <CardDescription>
            Detailed breakdown of security issues found
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {issues.map((issue, index) => (
              <motion.div
                key={issue.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border rounded-lg p-4"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    {getSeverityIcon(issue.severity)}
                    <Badge variant={getSeverityColor(issue.severity) as any}>
                      {issue.severity.toUpperCase()}
                    </Badge>
                  </div>
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
                
                <div className="bg-blue-50 dark:bg-blue-950/20 rounded-md p-3">
                  <p className="text-sm">
                    <span className="font-medium text-blue-700 dark:text-blue-300">
                      💡 Recommendation:
                    </span>{' '}
                    {issue.suggestion}
                  </p>
                </div>
              </motion.div>
            ))}
            
            {issues.length === 0 && (
              <div className="text-center py-8">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-green-700 dark:text-green-300 mb-2">
                  No Security Issues Found!
                </h3>
                <p className="text-muted-foreground">
                  Your code appears to be secure based on our analysis.
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
