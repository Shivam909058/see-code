import { motion } from 'framer-motion'
import { Brain, BarChart3, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card'

interface ComplexityReportProps {
  data: {
    quality_metrics: {
      cyclomatic_complexity?: number
      maintainability_index: number
    }
    language_stats: Array<{
      language: string
      complexity_score: number
      files_count: number
    }>
  }
}

export function ComplexityReport({ data }: ComplexityReportProps) {
  const getComplexityLevel = (score: number) => {
    if (score <= 5) return { level: 'Low', color: 'text-green-600', bgColor: 'bg-green-100' }
    if (score <= 10) return { level: 'Medium', color: 'text-yellow-600', bgColor: 'bg-yellow-100' }
    return { level: 'High', color: 'text-red-600', bgColor: 'bg-red-100' }
  }

  const avgComplexity = data.language_stats.reduce((acc, lang) => acc + lang.complexity_score, 0) / data.language_stats.length

  return (
    <div className="space-y-6">
      {/* Complexity Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Brain className="w-6 h-6 mr-2" />
            Complexity Analysis
          </CardTitle>
          <CardDescription>
            Code complexity and maintainability metrics
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold mb-2">
                {data.quality_metrics.maintainability_index.toFixed(1)}
              </div>
              <div className="text-sm text-muted-foreground">
                Maintainability Index
              </div>
              <div className="w-full bg-muted rounded-full h-2 mt-2">
                <div
                  className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full"
                  style={{ width: `${data.quality_metrics.maintainability_index}%` }}
                />
              </div>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold mb-2">
                {avgComplexity.toFixed(1)}
              </div>
              <div className="text-sm text-muted-foreground">
                Average Complexity
              </div>
              <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium mt-2 ${
                getComplexityLevel(avgComplexity).bgColor
              } ${getComplexityLevel(avgComplexity).color}`}>
                {getComplexityLevel(avgComplexity).level}
              </div>
            </div>

            <div className="text-center">
              <div className="text-3xl font-bold mb-2">
                {data.language_stats.length}
              </div>
              <div className="text-sm text-muted-foreground">
                Languages Analyzed
              </div>
              <div className="flex justify-center mt-2">
                <BarChart3 className="w-6 h-6 text-blue-500" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Language Complexity Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Complexity by Language</CardTitle>
          <CardDescription>
            Complexity scores for each programming language
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.language_stats.map((lang, index) => {
              const complexity = getComplexityLevel(lang.complexity_score)
              return (
                <motion.div
                  key={lang.language}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-center space-x-4">
                    <div className="font-medium">{lang.language}</div>
                    <div className="text-sm text-muted-foreground">
                      {lang.files_count} files
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="font-semibold">
                        {lang.complexity_score.toFixed(1)}
                      </div>
                      <div className={`text-xs ${complexity.color}`}>
                        {complexity.level}
                      </div>
                    </div>
                    
                    <div className="w-24 bg-muted rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          lang.complexity_score <= 5 ? 'bg-green-500' :
                          lang.complexity_score <= 10 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(lang.complexity_score * 10, 100)}%` }}
                      />
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <TrendingUp className="w-6 h-6 mr-2" />
            Complexity Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {avgComplexity > 10 && (
              <div className="flex items-start space-x-3 p-3 bg-red-50 dark:bg-red-950/20 rounded-lg">
                <div className="w-2 h-2 bg-red-500 rounded-full mt-2 flex-shrink-0" />
                <div>
                  <p className="font-medium text-red-700 dark:text-red-300">High Complexity Detected</p>
                  <p className="text-sm text-red-600 dark:text-red-400">
                    Consider breaking down complex functions and classes into smaller, more manageable pieces.
                  </p>
                </div>
              </div>
            )}
            
            {data.quality_metrics.maintainability_index < 70 && (
              <div className="flex items-start space-x-3 p-3 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg">
                <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2 flex-shrink-0" />
                <div>
                  <p className="font-medium text-yellow-700 dark:text-yellow-300">Maintainability Concerns</p>
                  <p className="text-sm text-yellow-600 dark:text-yellow-400">
                    Focus on improving code readability, adding documentation, and reducing complexity.
                  </p>
                </div>
              </div>
            )}
            
            {avgComplexity <= 5 && data.quality_metrics.maintainability_index >= 80 && (
              <div className="flex items-start space-x-3 p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0" />
                <div>
                  <p className="font-medium text-green-700 dark:text-green-300">Excellent Code Quality</p>
                  <p className="text-sm text-green-600 dark:text-green-400">
                    Your code maintains good complexity levels and high maintainability. Keep up the great work!
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}