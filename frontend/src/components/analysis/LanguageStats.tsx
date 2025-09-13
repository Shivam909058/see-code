import { motion } from 'framer-motion'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card'

interface Language {
  language: string
  files_count: number
  lines_of_code: number
  percentage: number
  complexity_score: number
}

interface LanguageStatsProps {
  languages: Language[]
}

export function LanguageStats({ languages }: LanguageStatsProps) {
  const getLanguageColor = (language: string) => {
    const colors: Record<string, string> = {
      'Python': '#3776ab',
      'JavaScript': '#f7df1e',
      'TypeScript': '#3178c6',
      'Java': '#ed8b00',
      'Go': '#00add8',
      'C++': '#00599c',
      'C#': '#239120',
      'Ruby': '#cc342d',
      'PHP': '#777bb4',
    }
    return colors[language] || '#6b7280'
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Language Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {languages.map((lang, index) => (
            <motion.div
              key={lang.language}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="space-y-2"
            >
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: getLanguageColor(lang.language) }}
                  />
                  <span className="font-medium">{lang.language}</span>
                </div>
                <span className="text-muted-foreground">
                  {lang.percentage.toFixed(1)}%
                </span>
              </div>
              
              <div className="w-full bg-muted rounded-full h-2">
                <motion.div
                  className="h-2 rounded-full"
                  style={{ backgroundColor: getLanguageColor(lang.language) }}
                  initial={{ width: 0 }}
                  animate={{ width: `${lang.percentage}%` }}
                  transition={{ duration: 0.8, delay: index * 0.1 }}
                />
              </div>
              
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{lang.files_count} files</span>
                <span>{lang.lines_of_code.toLocaleString()} lines</span>
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}


