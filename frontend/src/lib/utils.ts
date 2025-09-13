import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds.toFixed(1)}s`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}m ${remainingSeconds.toFixed(0)}s`
}

export function getSeverityColor(severity: string) {
  switch (severity.toLowerCase()) {
    case 'critical':
      return 'error'
    case 'high':
      return 'error'
    case 'medium':
      return 'warning'
    case 'low':
      return 'default'
    case 'info':
      return 'success'
    default:
      return 'default'
  }
}

export function getCategoryIcon(category: string) {
  switch (category.toLowerCase()) {
    case 'security':
      return '🔒'
    case 'performance':
      return '⚡'
    case 'complexity':
      return '🧠'
    case 'duplication':
      return '🔄'
    case 'testing':
      return '🧪'
    case 'documentation':
      return '📝'
    case 'maintainability':
      return '🔧'
    case 'style':
      return '🎨'
    default:
      return '📋'
  }
}