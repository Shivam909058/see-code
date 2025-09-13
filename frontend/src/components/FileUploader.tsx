import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, File, X, Play, Archive } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

import { Button } from './ui/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/Card'
import { LoadingSpinner } from './ui/LoadingSpinner'
import { Input } from './ui/Input'
import { Label } from './ui/Label'
import { analysisApi } from '@/lib/api'

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const ACCEPTED_TYPES = {
  'text/x-python': ['.py'],
  'application/javascript': ['.js'],
  'text/javascript': ['.js', '.jsx'],
  'application/typescript': ['.ts'],
  'text/typescript': ['.ts', '.tsx'],
  'text/x-java-source': ['.java'],
  'text/x-go': ['.go'],
  'text/x-c++src': ['.cpp', '.cc', '.cxx'],
  'text/x-csharp': ['.cs'],
  'application/zip': ['.zip'],
  'application/x-tar': ['.tar'],
  'application/gzip': ['.gz'],
  'application/x-gzip': ['.tar.gz']
}

export function FileUploader() {
  const [files, setFiles] = useState<File[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisName, setAnalysisName] = useState('')
  const navigate = useNavigate()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const validFiles = acceptedFiles.filter(file => {
      if (file.size > MAX_FILE_SIZE) {
        toast.error(`File "${file.name}" is too large. Maximum size is 10MB.`)
        return false
      }
      return true
    })

    setFiles(prev => [...prev, ...validFiles])
    
    // Auto-generate name if not set
    if (!analysisName && validFiles.length > 0) {
      const timestamp = new Date().toISOString().slice(0, 16).replace('T', ' ')
      setAnalysisName(`Code Analysis ${timestamp}`)
    }
  }, [analysisName])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    multiple: true
  })

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleAnalyze = async () => {
    if (files.length === 0) {
      toast.error('Please select at least one file')
      return
    }

    if (!analysisName.trim()) {
      toast.error('Please enter a name for your analysis')
      return
    }

    setIsAnalyzing(true)
    try {
      toast.success('Analysis started! Processing your files...')
      // Fixed: Pass the analysis name as the second parameter
      const response = await analysisApi.analyzeFiles(files, analysisName.trim())
      
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

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const totalSize = files.reduce((acc, file) => acc + file.size, 0)

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center">
          <Upload className="w-6 h-6 mr-2" />
          Upload Code Files
        </CardTitle>
        <CardDescription>
          Upload your code files for comprehensive analysis including security, performance, and quality insights.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Analysis Name Input */}
        <div className="space-y-2">
          <Label htmlFor="analysisName">Analysis Name</Label>
          <Input
            id="analysisName"
            placeholder="e.g., My Project Analysis"
            value={analysisName}
            onChange={(e) => setAnalysisName(e.target.value)}
            className="w-full"
          />
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/20'
              : 'border-muted-foreground/25 hover:border-muted-foreground/50'
          }`}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center space-y-4">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center">
              <Upload className="w-8 h-8 text-muted-foreground" />
            </div>
            {isDragActive ? (
              <div>
                <p className="text-lg font-medium">Drop files here</p>
                <p className="text-sm text-muted-foreground">
                  Release to upload your files
                </p>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium">Drag & drop files here</p>
                <p className="text-sm text-muted-foreground">
                  Or click to browse and select files
                </p>
                <p className="text-xs text-muted-foreground mt-2">
                  Supports: .py, .js, .ts, .java, .go, .cpp, .cs, .zip, .tar.gz (max 10MB each)
                </p>
              </div>
            )}
          </div>
        </div>

        {/* File List */}
        <AnimatePresence>
          {files.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Selected Files ({files.length})</h3>
                <p className="text-sm text-muted-foreground">
                  Total size: {formatFileSize(totalSize)}
                </p>
              </div>

              <div className="max-h-64 overflow-y-auto space-y-2">
                {files.map((file, index) => (
                  <motion.div
                    key={`${file.name}-${index}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      {file.type.includes('zip') || file.type.includes('tar') ? (
                        <Archive className="w-5 h-5 text-muted-foreground" />
                      ) : (
                        <File className="w-5 h-5 text-muted-foreground" />
                      )}
                      <div>
                        <p className="font-medium text-sm">{file.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {formatFileSize(file.size)}
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(index)}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Analyze Button */}
        <Button
          onClick={handleAnalyze}
          disabled={isAnalyzing || files.length === 0 || !analysisName.trim()}
          size="lg"
          className="w-full bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
        >
          {isAnalyzing ? (
            <>
              <LoadingSpinner size="sm" className="mr-2" />
              Analyzing Files...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Analyze {files.length} {files.length === 1 ? 'File' : 'Files'}
            </>
          )}
        </Button>

        {/* Info */}
        <div className="bg-muted/50 rounded-lg p-4">
          <h4 className="font-medium mb-2">Supported file types:</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm text-muted-foreground">
            <div>• Python (.py)</div>
            <div>• JavaScript (.js, .jsx)</div>
            <div>• TypeScript (.ts, .tsx)</div>
            <div>• Java (.java)</div>
            <div>• Go (.go)</div>
            <div>• C++ (.cpp, .cc)</div>
            <div>• C# (.cs)</div>
            <div>• Archives (.zip, .tar.gz)</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}