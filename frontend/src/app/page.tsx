'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Heart, Send, Upload, Activity, Clock, Phone, MapPin, FileText, 
  Sparkles, Bot, User, BarChart3, Mic, MicOff, AlertCircle, 
  CheckCircle, Calendar, Shield, Stethoscope, Brain, 
  Loader2, ChevronDown, ChevronUp, Info, FileCheck, X,
  Search, MessageSquare, TrendingUp, Users
} from 'lucide-react'
import ThemeToggle from '@/components/theme-toggle'
import { motion, AnimatePresence } from 'framer-motion'
import Image from 'next/image'

interface Citation {
  source: string
  title: string
  url: string
  snippet: string
}

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  citations?: Citation[]
  confidence?: number
  processingTime?: number
}

interface HealthMetric {
  label: string
  value: number
  unit: string
  trend: 'up' | 'down' | 'stable'
  color: string
}

interface QuickAction {
  icon: React.ElementType
  label: string
  query: string
  category: string
  color: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [mounted, setMounted] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [showCitations, setShowCitations] = useState<{ [key: string]: boolean }>({})
  const [uploadProgress, setUploadProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'connecting'>('connected')
  const [typingIndicator, setTypingIndicator] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const recognitionRef = useRef<any>(null)

  // Quick actions data
  const quickActions: QuickAction[] = [
    { icon: Calendar, label: 'Schedule Appointment', query: 'How do I schedule an appointment?', category: 'appointments', color: 'text-blue-600' },
    { icon: Stethoscope, label: 'Available Services', query: 'What services are available?', category: 'services', color: 'text-green-600' },
    { icon: Shield, label: 'Insurance Info', query: 'What insurance do you accept?', category: 'insurance', color: 'text-purple-600' },
    { icon: MapPin, label: 'Location & Hours', query: 'Where is the health center located?', category: 'location', color: 'text-red-600' },
    { icon: Brain, label: 'Mental Health', query: 'What mental health services are available?', category: 'mental-health', color: 'text-indigo-600' },
    { icon: Heart, label: 'Preventive Care', query: 'What preventive care services do you offer?', category: 'preventive', color: 'text-pink-600' }
  ]

  // Health metrics mock data
  const healthMetrics: HealthMetric[] = [
    { label: 'Response Time', value: 0.8, unit: 's', trend: 'down', color: 'text-green-600' },
    { label: 'Accuracy Rate', value: 98.5, unit: '%', trend: 'up', color: 'text-blue-600' },
    { label: 'Daily Queries', value: 1247, unit: '', trend: 'up', color: 'text-purple-600' },
    { label: 'User Satisfaction', value: 4.8, unit: '/5', trend: 'stable', color: 'text-yellow-600' }
  ]

  useEffect(() => {
    setMounted(true)
    
    // Initialize speech recognition
    if (typeof window !== 'undefined' && 'webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = 'en-US'
      
      recognitionRef.current.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((result: any) => result[0])
          .map((result: any) => result.transcript)
          .join('')
        
        setInput(transcript)
      }
      
      recognitionRef.current.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
      }
      
      recognitionRef.current.onend = () => {
        setIsListening(false)
      }
    }
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Toggle voice recognition
  const toggleVoiceRecognition = useCallback(() => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser.')
      return
    }

    if (isListening) {
      recognitionRef.current.stop()
    } else {
      recognitionRef.current.start()
      setIsListening(true)
    }
  }, [isListening])

  // Toggle citation visibility
  const toggleCitation = (messageId: string) => {
    setShowCitations(prev => ({
      ...prev,
      [messageId]: !prev[messageId]
    }))
  }

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setTypingIndicator(true)

    const startTime = Date.now()

    try {
      // Use the enhanced chat endpoint with citations
      const response = await fetch('/api/proxy/v1/chat/enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      const processingTime = (Date.now() - startTime) / 1000
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response || data.message || 'No response',
        role: 'assistant',
        timestamp: new Date(),
        citations: data.citations,
        confidence: data.confidence || 0.95,
        processingTime
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Play a subtle notification sound (optional)
      if ('Audio' in window) {
        const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBSp')
        audio.volume = 0.1
        audio.play().catch(() => {})
      }
    } catch (error) {
      console.error('Error:', error)
      const errorDetails = error instanceof Error ? error.message : 'Unknown error'
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: `I apologize for the inconvenience. I'm having trouble connecting to the server. Please try again in a moment or contact support at 412-268-2157.`,
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
      setConnectionStatus('disconnected')
    } finally {
      setIsLoading(false)
      setTypingIndicator(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // File size validation (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: `File size exceeds 10MB limit. Please upload a smaller file.`,
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    setUploadStatus('uploading')
    setUploadProgress(0)

    // Simulate progress for better UX
    const progressInterval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval)
          return prev
        }
        return prev + 10
      })
    }, 200)

    try {
      const response = await fetch('/api/proxy/v1/documents/upload', {
        method: 'POST',
        body: formData
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (response.ok) {
        setUploadStatus('success')
        const successMessage: Message = {
          id: Date.now().toString(),
          content: `✅ Successfully uploaded ${file.name}. The document has been processed and added to my knowledge base. I can now answer questions about its content.`,
          role: 'assistant',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, successMessage])
        
        // Reset upload status after 3 seconds
        setTimeout(() => {
          setUploadStatus('idle')
          setUploadProgress(0)
        }, 3000)
      } else {
        throw new Error(`Upload failed with status: ${response.status}`)
      }
    } catch (error) {
      clearInterval(progressInterval)
      setUploadStatus('error')
      console.error('Upload error:', error)
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: `❌ Failed to upload ${file.name}. Please ensure the file is in a supported format (PDF, TXT, or MD) and try again.`,
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
      
      // Reset upload status after 3 seconds
      setTimeout(() => {
        setUploadStatus('idle')
        setUploadProgress(0)
      }, 3000)
    }
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  if (!mounted) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <header className="border-b bg-white/95 dark:bg-gray-900/95 backdrop-blur-lg sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 py-3 md:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 md:space-x-4">
              <Image 
                src="/cmu-logo.png" 
                alt="Carnegie Mellon University" 
                width={150} 
                height={35}
                className="dark:invert md:w-[180px] md:h-[40px]"
              />
              <div className="border-l pl-2 md:pl-4 ml-2">
                <h1 className="text-lg md:text-2xl font-bold text-gray-900 dark:text-white">Health Services</h1>
                <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400 flex items-center">
                  <Bot className="h-3 w-3 mr-1" />
                  AI Health Assistant
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2 md:space-x-4">
              {/* Connection Status Indicator */}
              <div className="flex items-center space-x-1">
                <div className={`w-2 h-2 rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-500' : 
                  connectionStatus === 'connecting' ? 'bg-yellow-500 animate-pulse' : 
                  'bg-red-500'
                }`} />
                <span className="text-xs text-gray-600 dark:text-gray-400 hidden sm:inline">
                  {connectionStatus === 'connected' ? 'Connected' : 
                   connectionStatus === 'connecting' ? 'Connecting...' : 
                   'Disconnected'}
                </span>
              </div>
              
              <Button
                variant="outline"
                className="flex items-center space-x-2 text-sm"
                onClick={() => window.location.href = '/analytics'}
              >
                <BarChart3 className="h-4 w-4" />
                <span className="hidden sm:inline">Analytics</span>
              </Button>
              
              <Button variant="outline" className="hidden lg:flex items-center space-x-2 text-sm">
                <Phone className="h-4 w-4" />
                <span>412-268-2157</span>
              </Button>
              
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-4 md:py-8">
        {/* Health Metrics Dashboard */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {healthMetrics.map((metric, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-gray-200 dark:border-gray-700">
                <CardContent className="p-3 md:p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs md:text-sm text-gray-600 dark:text-gray-400">{metric.label}</p>
                      <p className={`text-lg md:text-2xl font-bold ${metric.color}`}>
                        {metric.value}{metric.unit}
                      </p>
                    </div>
                    <div className={`${metric.color} opacity-50`}>
                      {metric.trend === 'up' ? <TrendingUp className="h-5 w-5" /> :
                       metric.trend === 'down' ? <ChevronDown className="h-5 w-5" /> :
                       <Activity className="h-5 w-5" />}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            {/* Quick Actions */}
            <Card className="border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="bg-gradient-to-br from-blue-600 to-green-600 text-white rounded-t-lg">
                <CardTitle className="text-lg flex items-center">
                  <Sparkles className="mr-2 h-5 w-5 animate-pulse" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 pt-4">
                {quickActions.map((action, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                  >
                    <Button 
                      variant="outline" 
                      className={`w-full justify-start hover:bg-gradient-to-r hover:from-blue-50 hover:to-green-50 dark:hover:from-gray-800 dark:hover:to-gray-700 hover:border-blue-300 transition-all duration-200 group`}
                      onClick={() => {
                        setInput(action.query)
                        sendMessage()
                      }}
                    >
                      <action.icon className={`mr-2 h-4 w-4 ${action.color} group-hover:scale-110 transition-transform`} />
                      <span className="text-sm">{action.label}</span>
                    </Button>
                  </motion.div>
                ))}
              </CardContent>
            </Card>

            {/* Upload Document */}
            <Card className="border-gray-200 dark:border-gray-700 shadow-lg">
              <CardHeader className="bg-gradient-to-br from-purple-100 to-blue-100 dark:from-gray-800 dark:to-gray-700">
                <CardTitle className="text-lg flex items-center">
                  <FileCheck className="mr-2 h-5 w-5 text-purple-600" />
                  Document Upload
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-4">
                <Button
                  variant="outline"
                  className="w-full hover:border-purple-300 hover:bg-purple-50 dark:hover:bg-gray-700"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadStatus === 'uploading'}
                >
                  {uploadStatus === 'uploading' ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Uploading... {uploadProgress}%
                    </>
                  ) : uploadStatus === 'success' ? (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2 text-green-600" />
                      Upload Complete!
                    </>
                  ) : uploadStatus === 'error' ? (
                    <>
                      <AlertCircle className="h-4 w-4 mr-2 text-red-600" />
                      Upload Failed
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Document
                    </>
                  )}
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.txt,.md"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                {uploadStatus === 'uploading' && (
                  <div className="mt-2">
                    <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                      <div 
                        className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${uploadProgress}%` }}
                      />
                    </div>
                  </div>
                )}
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">
                  Supported: PDF, TXT, MD (max 10MB)
                </p>
              </CardContent>
            </Card>

            {/* Contact Info */}
            <Card className="border-gray-200 dark:border-gray-700 shadow-lg">
              <CardHeader className="bg-gradient-to-br from-green-100 to-blue-100 dark:from-gray-800 dark:to-gray-700">
                <CardTitle className="text-lg flex items-center">
                  <Info className="mr-2 h-5 w-5 text-green-600" />
                  Contact & Hours
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm pt-4">
                <div className="flex items-start space-x-2">
                  <MapPin className="h-4 w-4 text-blue-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium">Location</p>
                    <p className="text-gray-600 dark:text-gray-400">1060 Morewood Avenue</p>
                    <p className="text-gray-600 dark:text-gray-400">Pittsburgh, PA 15213</p>
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <Phone className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium">Phone</p>
                    <p className="text-gray-600 dark:text-gray-400">412-268-2157</p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">24/7 Nurse Line Available</p>
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <Clock className="h-4 w-4 text-purple-500 mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="font-medium">Hours</p>
                    <p className="text-gray-600 dark:text-gray-400">Mon-Fri: 8:30 AM - 5:00 PM</p>
                    <p className="text-gray-600 dark:text-gray-400">Sat-Sun: Closed</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-[75vh] flex flex-col shadow-2xl border-gray-200 dark:border-gray-700 overflow-hidden">
              <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-green-50 dark:from-gray-800 dark:to-gray-700">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <motion.div 
                      className="relative"
                      animate={{ rotate: [0, 10, -10, 0] }}
                      transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                    >
                      <Bot className="h-8 w-8 text-blue-600" />
                      <Sparkles className="h-3 w-3 text-yellow-500 absolute -top-1 -right-1 animate-pulse" />
                    </motion.div>
                    <div>
                      <CardTitle className="text-xl">CMU Health Assistant</CardTitle>
                      <CardDescription className="flex items-center gap-2">
                        <span>Powered by AI • Available 24/7</span>
                        {typingIndicator && (
                          <span className="flex items-center text-xs text-blue-600">
                            <Loader2 className="h-3 w-3 animate-spin mr-1" />
                            typing...
                          </span>
                        )}
                      </CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setMessages([])}
                      className="hover:bg-red-50 hover:border-red-300"
                    >
                      <X className="h-4 w-4" />
                      <span className="hidden sm:inline ml-2">Clear</span>
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-4 bg-gradient-to-b from-white to-gray-50 dark:from-gray-800 dark:to-gray-900">
                <AnimatePresence mode="wait">
                  {messages.length === 0 ? (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center h-full text-center p-4"
                    >
                      <motion.div
                        animate={{ scale: [1, 1.1, 1] }}
                        transition={{ duration: 2, repeat: Infinity }}
                      >
                        <Heart className="h-20 w-20 text-blue-500 mb-6" />
                      </motion.div>
                      <h3 className="text-2xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
                        Welcome to CMU Health Services
                      </h3>
                      <p className="text-gray-600 dark:text-gray-400 max-w-lg mb-6">
                        I'm your AI health assistant, here to help with appointments, insurance, health services, and more. 
                        All information is based on official CMU Health Services data.
                      </p>
                      <div className="grid grid-cols-2 gap-3 max-w-md">
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          className="p-3 bg-blue-50 dark:bg-gray-700 rounded-lg cursor-pointer"
                          onClick={() => setInput('What services are available?')}
                        >
                          <Stethoscope className="h-6 w-6 text-blue-600 mx-auto mb-1" />
                          <p className="text-sm font-medium">Services</p>
                        </motion.div>
                        <motion.div
                          whileHover={{ scale: 1.05 }}
                          className="p-3 bg-green-50 dark:bg-gray-700 rounded-lg cursor-pointer"
                          onClick={() => setInput('How do I schedule an appointment?')}
                        >
                          <Calendar className="h-6 w-6 text-green-600 mx-auto mb-1" />
                          <p className="text-sm font-medium">Appointments</p>
                        </motion.div>
                      </div>
                    </motion.div>
                  ) : (
                    <div className="space-y-4">
                      {messages.map((message, messageIdx) => (
                        <motion.div
                          key={message.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: messageIdx * 0.05 }}
                          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`flex items-start space-x-3 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                            <motion.div 
                              className={`p-2 rounded-full flex-shrink-0 ${
                                message.role === 'user' 
                                  ? 'bg-gradient-to-br from-blue-600 to-green-600' 
                                  : 'bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600'
                              }`}
                              whileHover={{ scale: 1.1 }}
                            >
                              {message.role === 'user' ? (
                                <User className="h-5 w-5 text-white" />
                              ) : (
                                <Bot className="h-5 w-5 text-gray-700 dark:text-gray-200" />
                              )}
                            </motion.div>
                            <div className="space-y-1">
                              <div className={`px-4 py-3 rounded-2xl shadow-sm ${
                                message.role === 'user' 
                                  ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white' 
                                  : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-700'
                              }`}>
                                <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
                                <div className={`flex items-center justify-between mt-2 text-xs ${
                                  message.role === 'user' ? 'text-blue-200' : 'text-gray-500 dark:text-gray-400'
                                }`}>
                                  <span>{message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                  {message.processingTime && (
                                    <span className="ml-2">⚡ {message.processingTime.toFixed(1)}s</span>
                                  )}
                                  {message.confidence && message.role === 'assistant' && (
                                    <span className="ml-2">📊 {(message.confidence * 100).toFixed(0)}%</span>
                                  )}
                                </div>
                              </div>
                              
                              {/* Citations */}
                              {message.citations && message.citations.length > 0 && (
                                <motion.div 
                                  initial={{ opacity: 0, height: 0 }}
                                  animate={{ opacity: 1, height: 'auto' }}
                                  className="mt-2"
                                >
                                  <button
                                    onClick={() => toggleCitation(message.id)}
                                    className="flex items-center text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 mb-2"
                                  >
                                    <FileText className="h-3 w-3 mr-1" />
                                    {showCitations[message.id] ? 'Hide' : 'Show'} {message.citations.length} source{message.citations.length > 1 ? 's' : ''}
                                    {showCitations[message.id] ? <ChevronUp className="h-3 w-3 ml-1" /> : <ChevronDown className="h-3 w-3 ml-1" />}
                                  </button>
                                  
                                  <AnimatePresence>
                                    {showCitations[message.id] && (
                                      <motion.div
                                        initial={{ opacity: 0, y: -10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        exit={{ opacity: 0, y: -10 }}
                                        className="space-y-2"
                                      >
                                        {message.citations.map((citation, idx) => (
                                          <motion.div 
                                            key={idx} 
                                            className="bg-gradient-to-r from-blue-50 to-green-50 dark:from-gray-800 dark:to-gray-700 p-3 rounded-lg border border-blue-200 dark:border-gray-600"
                                            whileHover={{ scale: 1.02 }}
                                          >
                                            <a 
                                              href={citation.url} 
                                              target="_blank" 
                                              rel="noopener noreferrer"
                                              className="text-sm font-medium text-blue-700 dark:text-blue-400 hover:underline flex items-center"
                                            >
                                              <FileCheck className="h-3 w-3 mr-1" />
                                              {citation.title}
                                            </a>
                                            <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                                              {citation.snippet}
                                            </p>
                                          </motion.div>
                                        ))}
                                      </motion.div>
                                    )}
                                  </AnimatePresence>
                                </motion.div>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      ))}
                      {/* Typing Indicator */}
                      {typingIndicator && (
                        <motion.div
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="flex justify-start"
                        >
                          <div className="flex items-start space-x-3">
                            <div className="p-2 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600">
                              <Bot className="h-5 w-5 text-gray-700 dark:text-gray-200" />
                            </div>
                            <div className="bg-white dark:bg-gray-800 rounded-2xl px-4 py-3 shadow-sm border border-gray-200 dark:border-gray-700">
                              <div className="flex items-center space-x-1">
                                <motion.div
                                  animate={{ opacity: [0.4, 1, 0.4] }}
                                  transition={{ duration: 1.5, repeat: Infinity }}
                                  className="w-2 h-2 bg-blue-600 rounded-full"
                                />
                                <motion.div
                                  animate={{ opacity: [0.4, 1, 0.4] }}
                                  transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                                  className="w-2 h-2 bg-blue-600 rounded-full"
                                />
                                <motion.div
                                  animate={{ opacity: [0.4, 1, 0.4] }}
                                  transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                                  className="w-2 h-2 bg-blue-600 rounded-full"
                                />
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </AnimatePresence>
              </CardContent>
              
              {/* Input Area */}
              <CardFooter className="border-t bg-gradient-to-r from-gray-50 to-white dark:from-gray-800 dark:to-gray-700 p-4">
                <form onSubmit={sendMessage} className="flex w-full space-x-2">
                  <div className="flex-1 relative">
                    <input
                      type="text"
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      placeholder="Ask about health services, appointments, insurance..."
                      className="w-full px-4 py-3 pr-12 border-2 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 dark:bg-gray-800 dark:border-gray-600 dark:focus:ring-blue-600 dark:focus:border-blue-600 transition-all"
                      disabled={isLoading}
                    />
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full p-2 hover:bg-gray-100 dark:hover:bg-gray-700"
                      onClick={toggleVoiceRecognition}
                      disabled={isLoading}
                    >
                      {isListening ? (
                        <MicOff className="h-4 w-4 text-red-600 animate-pulse" />
                      ) : (
                        <Mic className="h-4 w-4 text-gray-600 dark:text-gray-400" />
                      )}
                    </Button>
                  </div>
                  <Button 
                    type="submit" 
                    disabled={isLoading || !input.trim()}
                    className="rounded-full bg-gradient-to-r from-blue-600 to-green-600 hover:from-blue-700 hover:to-green-700 text-white px-6"
                  >
                    {isLoading ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <Send className="h-5 w-5" />
                    )}
                  </Button>
                </form>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
                  Press Enter to send • {recognitionRef.current ? 'Click mic for voice input' : 'Voice input not supported'}
                </p>
              </CardFooter>
            </Card>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 border-t mt-8">
        <div className="container mx-auto px-4 py-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="text-center md:text-left">
              <p className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Emergency</p>
              <p className="text-gray-600 dark:text-gray-400">For emergencies, call 911</p>
              <p className="text-gray-600 dark:text-gray-400">CMU Police: 412-268-2323</p>
            </div>
            <div className="text-center">
              <p className="font-semibold text-gray-700 dark:text-gray-300 mb-2">Quick Links</p>
              <div className="flex justify-center space-x-4">
                <a href="#" className="text-blue-600 hover:text-blue-700 dark:text-blue-400">Health Portal</a>
                <a href="#" className="text-blue-600 hover:text-blue-700 dark:text-blue-400">Insurance</a>
                <a href="#" className="text-blue-600 hover:text-blue-700 dark:text-blue-400">Forms</a>
              </div>
            </div>
            <div className="text-center md:text-right">
              <p className="text-gray-600 dark:text-gray-400">
                © {new Date().getFullYear()} Carnegie Mellon University
              </p>
              <p className="text-gray-500 dark:text-gray-500 text-xs mt-1">
                Made with <Heart className="h-3 w-3 text-red-500 inline" /> by <strong>Siva Komaragiri</strong>
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}