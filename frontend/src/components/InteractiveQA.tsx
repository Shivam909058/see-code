import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, X, MessageSquare, Bot, User, Lightbulb, Copy, Check } from 'lucide-react'
import { Button } from './ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card'
import { LoadingSpinner } from './ui/LoadingSpinner'
import { MarkdownRenderer } from './ui/MarkdownRenderer'
import { analysisApi } from '@/lib/api'
import toast from 'react-hot-toast'

interface Message {
  id: string
  type: 'user' | 'assistant'
  content: string
  timestamp: Date
  followUpQuestions?: string[]
}

interface InteractiveQAProps {
  analysisId: string
  onClose?: () => void
}

export function InteractiveQA({ analysisId, onClose }: InteractiveQAProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: `# Welcome to Your AI Code Assistant! 🤖

I've analyzed your codebase and I'm ready to help you understand it better. I can provide insights about:

- **Security vulnerabilities** and how to fix them
- **Performance bottlenecks** and optimization opportunities  
- **Code quality issues** and best practices
- **Architecture patterns** and design improvements
- **Testing strategies** and coverage gaps
- **Documentation** suggestions

Feel free to ask me anything about your code using natural language!`,
      timestamp: new Date(),
      followUpQuestions: [
        "What are the main security issues in my code?",
        "How can I improve the performance?",
        "What's the overall code quality score?",
        "Are there any architectural concerns?",
        "What testing gaps should I address?",
        "Show me the most complex functions"
      ]
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await analysisApi.askQuestion(message, analysisId)
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.data.answer,
        timestamp: new Date(),
        followUpQuestions: response.data.follow_up_questions
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      toast.error('Failed to get response. Please try again.')
      console.error('Q&A error:', error)
      
      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `❌ **Sorry, I encountered an error while processing your question.**

This might be due to:
- Temporary server issues
- Network connectivity problems
- Analysis data not being fully loaded

Please try asking your question again, or try a simpler question first.`,
        timestamp: new Date(),
        followUpQuestions: [
          "What is the main purpose of this codebase?",
          "How many files were analyzed?",
          "What programming languages are used?"
        ]
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuestionClick = (question: string) => {
    handleSendMessage(question)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    handleSendMessage(input)
  }

  const copyToClipboard = async (content: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(content)
      setCopiedMessageId(messageId)
      toast.success('Copied to clipboard!')
      setTimeout(() => setCopiedMessageId(null), 2000)
    } catch (err) {
      toast.error('Failed to copy to clipboard')
    }
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center">
            <MessageSquare className="w-5 h-5 mr-2" />
            AI Code Assistant
          </CardTitle>
          {onClose && (
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-muted text-foreground border'
                  }`}
                >
                  <div className="flex items-start space-x-2 p-3">
                    {message.type === 'assistant' && (
                      <Bot className="w-4 h-4 mt-1 flex-shrink-0 text-blue-600" />
                    )}
                    {message.type === 'user' && (
                      <User className="w-4 h-4 mt-1 flex-shrink-0" />
                    )}
                    <div className="flex-1 min-w-0">
                      {message.type === 'user' ? (
                        <p className="text-sm whitespace-pre-wrap break-words">{message.content}</p>
                      ) : (
                        <MarkdownRenderer 
                          content={message.content} 
                          className="text-sm"
                        />
                      )}
                      <div className="flex items-center justify-between mt-2">
                        <p className={`text-xs ${
                          message.type === 'user' ? 'text-blue-100' : 'text-muted-foreground'
                        }`}>
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                        {message.type === 'assistant' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(message.content, message.id)}
                            className={`h-6 px-2 ${
                              message.type === 'user' ? 'text-blue-100 hover:text-white' : ''
                            }`}
                          >
                            {copiedMessageId === message.id ? (
                              <Check className="w-3 h-3" />
                            ) : (
                              <Copy className="w-3 h-3" />
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Follow-up Questions */}
                  {message.followUpQuestions && message.followUpQuestions.length > 0 && (
                    <div className="mx-3 pb-3 pt-0 border-t border-muted-foreground/20">
                      <div className="flex items-center space-x-1 mb-2 mt-2">
                        <Lightbulb className="w-3 h-3 text-amber-500" />
                        <span className="text-xs font-medium">Suggested questions:</span>
                      </div>
                      <div className="space-y-1">
                        {message.followUpQuestions.map((question, index) => (
                          <button
                            key={index}
                            onClick={() => handleQuestionClick(question)}
                            className="block w-full text-left text-xs p-2 rounded bg-background/50 hover:bg-background/80 transition-colors border border-muted-foreground/10 hover:border-muted-foreground/20"
                            disabled={isLoading}
                          >
                            {question}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="bg-muted rounded-lg p-3 flex items-center space-x-2 border">
                <Bot className="w-4 h-4 text-blue-600" />
                <LoadingSpinner size="sm" />
                <span className="text-sm text-muted-foreground">Analyzing your question...</span>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t p-4">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about your code... (supports markdown and LaTeX)"
              className="flex-1 px-3 py-2 border border-input rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
              disabled={isLoading}
            />
            <Button type="submit" size="sm" disabled={!input.trim() || isLoading}>
              <Send className="w-4 h-4" />
            </Button>
          </form>
          <p className="text-xs text-muted-foreground mt-2">
            💡 Try asking: "Explain the security issues", "Show me performance problems", or "What's the code complexity?"
          </p>
        </div>
      </CardContent>
    </Card>
  )
}


