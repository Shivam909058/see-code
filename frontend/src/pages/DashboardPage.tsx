import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Upload, 
  Github, 
  Code2, 
  History, 
  LogOut,
  Plus,
  Search,
  Filter
} from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card'
import { useAuthStore } from '@/stores/auth'
import { RepositoryAnalyzer } from '@/components/RepositoryAnalyzer'
import { FileUploader } from '@/components/FileUploader'
import { AnalysisHistory } from '@/components/AnalysisHistory'
import { UserProfile } from '@/components/UserProfile'

type AnalysisMode = 'repository' | 'upload' | 'history'

export function DashboardPage() {
  const { user, logout } = useAuthStore()
  const [activeMode, setActiveMode] = useState<AnalysisMode>('repository')

  const modes = [
    {
      id: 'repository' as const,
      title: 'GitHub Repository',
      description: 'Analyze any public GitHub repository',
      icon: Github,
      color: 'from-blue-500 to-blue-600'
    },
    {
      id: 'upload' as const,
      title: 'Upload Files',
      description: 'Upload code files or archives',
      icon: Upload,
      color: 'from-green-500 to-green-600'
    },
    {
      id: 'history' as const,
      title: 'Analysis History',
      description: 'View your previous analyses',
      icon: History,
      color: 'from-purple-500 to-purple-600'
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Code2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Quantum Code Inspector</h1>
              <p className="text-sm text-muted-foreground">AI-Powered Code Analysis</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <UserProfile user={user} />
            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              className="text-muted-foreground hover:text-foreground"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-3xl font-bold mb-2">
            Welcome back, {user?.github_username || 'Developer'}! 👋
          </h2>
          <p className="text-muted-foreground text-lg">
            Ready to analyze some code? Choose your preferred method below.
          </p>
        </motion.div>

        {/* Mode Selection */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {modes.map((mode, index) => (
            <motion.div
              key={mode.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card
                className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                  activeMode === mode.id 
                    ? 'ring-2 ring-blue-500 shadow-lg' 
                    : 'hover:shadow-md'
                }`}
                onClick={() => setActiveMode(mode.id)}
              >
                <CardHeader className="text-center">
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${mode.color} flex items-center justify-center mx-auto mb-4`}>
                    <mode.icon className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle className="text-lg">{mode.title}</CardTitle>
                  <CardDescription>{mode.description}</CardDescription>
                </CardHeader>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Analysis Interface */}
        <motion.div
          key={activeMode}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeMode === 'repository' && <RepositoryAnalyzer />}
          {activeMode === 'upload' && <FileUploader />}
          {activeMode === 'history' && <AnalysisHistory />}
        </motion.div>
      </div>
    </div>
  )
}