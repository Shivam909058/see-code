import { useState } from 'react'
import { motion } from 'framer-motion'
import { Filter, Search, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { getSeverityColor, getCategoryIcon } from '@/lib/utils'

interface Issue {
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
}

interface IssuesTableProps {
  issues: Issue[]
}

export function IssuesTable({ issues }: IssuesTableProps) {
  const [filter, setFilter] = useState<string>('all')
  const [search, setSearch] = useState('')

  const filteredIssues = issues.filter(issue => {
    const matchesFilter = filter === 'all' || issue.severity === filter
    const matchesSearch = search === '' || 
      issue.title.toLowerCase().includes(search.toLowerCase()) ||
      issue.file_path.toLowerCase().includes(search.toLowerCase())
    
    return matchesFilter && matchesSearch
  })

  const severityOptions = ['all', 'critical', 'high', 'medium', 'low', 'info']

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Issues Found</CardTitle>
            <CardDescription>
              {filteredIssues.length} of {issues.length} issues
            </CardDescription>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search issues..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10 pr-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              />
            </div>
            
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 border border-input rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
            >
              {severityOptions.map(option => (
                <option key={option} value={option}>
                  {option === 'all' ? 'All Severities' : option.charAt(0).toUpperCase() + option.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <div className="space-y-4">
          {filteredIssues.map((issue, index) => (
            <motion.div
              key={issue.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <Badge variant={getSeverityColor(issue.severity) as any}>
                      {issue.severity}
                    </Badge>
                    <span className="text-sm">{getCategoryIcon(issue.category)}</span>
                    <span className="text-sm text-muted-foreground capitalize">
                      {issue.category}
                    </span>
                  </div>
                  
                  <h3 className="font-semibold mb-2">{issue.title}</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    {issue.description}
                  </p>
                  
                  <div className="flex items-center space-x-4 text-xs text-muted-foreground mb-3">
                    <span>{issue.file_path}</span>
                    {issue.line_number && <span>Line {issue.line_number}</span>}
                    <span>Impact: {issue.impact_score.toFixed(1)}/10</span>
                    <span>Confidence: {(issue.confidence * 100).toFixed(0)}%</span>
                  </div>
                  
                  <div className="bg-blue-50 dark:bg-blue-950/20 rounded-md p-3">
                    <p className="text-sm">
                      <span className="font-medium">Suggestion: </span>
                      {issue.suggestion}
                    </p>
                  </div>
                </div>
                
                <Button variant="ghost" size="sm">
                  <ExternalLink className="w-4 h-4" />
                </Button>
              </div>
            </motion.div>
          ))}
          
          {filteredIssues.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">
              No issues found matching your criteria.
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
