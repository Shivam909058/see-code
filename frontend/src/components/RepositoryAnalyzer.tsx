import { useState } from 'react'
import { motion } from 'framer-motion'
import { Github, Play, GitBranch, ExternalLink } from 'lucide-react'
import { Button } from './ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'
import { LoadingSpinner } from './ui/LoadingSpinner'
import { analysisApi } from '@/lib/api'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export function RepositoryAnalyzer() {
  const [repoUrl, setRepoUrl] = useState('')
  const [branch, setBranch] = useState('main')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const navigate = useNavigate()

  const handleAnalyze = async () => {
    if (!repoUrl.trim()) {
      toast.error('Please enter a repository URL')
      return
    }

    // Validate GitHub URL
    const githubRegex = /^https:\/\/github\.com\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\/?$/
    if (!githubRegex.test(repoUrl.trim())) {
      toast.error('Please enter a valid GitHub repository URL')
      return
    }

    setIsAnalyzing(true)
    try {
      toast.success('Analysis started! This may take a few minutes...')
      // FIXED: Pass branch as second parameter
      const response = await analysisApi.analyzeRepository(repoUrl.trim(), branch.trim() || 'main')
      
      // Navigate to analysis results
      navigate(`/analysis/${response.data.analysis_id}`)
    } catch (error: any) {
      console.error('Analysis failed:', error)
      const message = error.response?.data?.detail || 'Analysis failed. Please try again.'
      toast.error(message)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const popularRepos = [
    {
      name: 'facebook/react',
      description: 'The library for web and native user interfaces',
      url: 'https://github.com/facebook/react'
    },
    {
      name: 'microsoft/vscode',
      description: 'Visual Studio Code',
      url: 'https://github.com/microsoft/vscode'
    },
    {
      name: 'vercel/next.js',
      description: 'The React Framework',
      url: 'https://github.com/vercel/next.js'
    }
  ]

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center">
          <Github className="w-6 h-6 mr-2" />
          Analyze GitHub Repository
        </CardTitle>
        <CardDescription>
          Enter any public GitHub repository URL to start a comprehensive code quality analysis
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* URL Input */}
        <div className="space-y-2">
          <label htmlFor="repo-url" className="text-sm font-medium">
            Repository URL
          </label>
          <div className="flex space-x-2">
            <input
              id="repo-url"
              type="url"
              placeholder="https://github.com/owner/repository"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              disabled={isAnalyzing}
            />
          </div>
        </div>

        {/* Branch Input */}
        <div className="space-y-2">
          <label htmlFor="branch" className="text-sm font-medium">
            Branch (optional)
          </label>
          <div className="flex space-x-2">
            <div className="relative flex-1">
              <GitBranch className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                id="branch"
                type="text"
                placeholder="main"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                className="pl-10 pr-3 py-2 w-full border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                disabled={isAnalyzing}
              />
            </div>
          </div>
        </div>

        {/* Analyze Button */}
        <Button
          onClick={handleAnalyze}
          disabled={isAnalyzing || !repoUrl.trim()}
          size="lg"
          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          {isAnalyzing ? (
            <>
              <LoadingSpinner size="sm" className="mr-2" />
              Analyzing Repository...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Start Analysis
            </>
          )}
        </Button>

        {/* Popular Repositories */}
        <div className="pt-6 border-t">
          <h3 className="text-sm font-medium mb-4 text-muted-foreground">
            Try these popular repositories:
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {popularRepos.map((repo) => (
              <motion.div
                key={repo.name}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card 
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => setRepoUrl(repo.url)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-sm">{repo.name}</h4>
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                          {repo.description}
                        </p>
                      </div>
                      <ExternalLink className="w-4 h-4 text-muted-foreground ml-2" />
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Analysis Info */}
        <div className="bg-muted/50 rounded-lg p-4">
          <h4 className="font-medium mb-2">What we'll analyze:</h4>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• Security vulnerabilities and OWASP Top 10 issues</li>
            <li>• Performance bottlenecks and optimization opportunities</li>
            <li>• Code complexity and maintainability metrics</li>
            <li>• Code duplication and architectural issues</li>
            <li>• Documentation coverage and testing gaps</li>
            <li>• Multi-language support with AST parsing</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  )
}