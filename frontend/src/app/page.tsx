'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Heart, Send, Upload, Activity, Clock, Phone, MapPin, FileText, Sparkles, Bot, User, BarChart3 } from 'lucide-react'
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
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [mounted, setMounted] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
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

    try {
      const response = await fetch('/api/proxy/v2/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })

      const data = await response.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response || data.message || 'No response',
        role: 'assistant',
        timestamp: new Date(),
        citations: data.citations
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, I encountered an error. Please try again.',
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('/api/proxy/v1/documents/upload', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const successMessage: Message = {
          id: Date.now().toString(),
          content: `Successfully uploaded ${file.name}. The document has been added to my knowledge base.`,
          role: 'assistant',
          timestamp: new Date()
        }
        setMessages(prev => [...prev, successMessage])
      }
    } catch (error) {
      console.error('Upload error:', error)
    }
  }

  if (!mounted) {
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-gray-50 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="border-b bg-white/90 dark:bg-gray-900/90 backdrop-blur-md sticky top-0 z-50 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Image 
                src="/cmu-logo.png" 
                alt="Carnegie Mellon University" 
                width={180} 
                height={40}
                className="dark:invert"
              />
              <div className="border-l pl-4 ml-2">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Health Services</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">AI-Powered Health Assistant</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button 
                variant="outline" 
                className="flex items-center space-x-2"
                onClick={() => window.location.href = '/analytics'}
              >
                <BarChart3 className="h-4 w-4" />
                <span>Analytics</span>
              </Button>
              <Button variant="outline" className="hidden md:flex items-center space-x-2">
                <Phone className="h-4 w-4" />
                <span>412-268-2157</span>
              </Button>
              <Button variant="outline" className="hidden md:flex items-center space-x-2">
                <Clock className="h-4 w-4" />
                <span>Mon-Fri: 8:30 AM - 5:00 PM</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            {/* Quick Actions */}
            <Card className="border-gray-200 shadow-sm hover:shadow-md transition-shadow">
              <CardHeader className="bg-gradient-to-r from-red-600 to-red-700 text-white">
                <CardTitle className="text-lg flex items-center">
                  <Sparkles className="mr-2 h-5 w-5" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 pt-4">
                <Button 
                  variant="outline" 
                  className="w-full justify-start hover:bg-red-50 hover:text-red-700 hover:border-red-300 transition-colors" 
                  onClick={() => setInput('How do I schedule an appointment?')}
                >
                  <Activity className="mr-2 h-4 w-4" />
                  Schedule Appointment
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start hover:bg-red-50 hover:text-red-700 hover:border-red-300 transition-colors" 
                  onClick={() => setInput('What services are available?')}
                >
                  <Heart className="mr-2 h-4 w-4" />
                  Available Services
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start hover:bg-red-50 hover:text-red-700 hover:border-red-300 transition-colors" 
                  onClick={() => setInput('What insurance do you accept?')}
                >
                  <FileText className="mr-2 h-4 w-4" />
                  Insurance Info
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full justify-start hover:bg-red-50 hover:text-red-700 hover:border-red-300 transition-colors" 
                  onClick={() => setInput('Where is the health center located?')}
                >
                  <MapPin className="mr-2 h-4 w-4" />
                  Location & Hours
                </Button>
              </CardContent>
            </Card>

            {/* Contact Info */}
            <Card className="border-gray-200 shadow-sm">
              <CardHeader className="bg-gray-50 dark:bg-gray-800">
                <CardTitle className="text-lg flex items-center">
                  <Phone className="mr-2 h-5 w-5 text-red-600" />
                  Contact Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div className="flex items-start space-x-2">
                  <MapPin className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <p className="font-medium">Location</p>
                    <p className="text-gray-600 dark:text-gray-400">Highmark location only</p>
                    <p className="text-gray-600 dark:text-gray-400">Pittsburgh, PA 15213</p>
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <Phone className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <p className="font-medium">Phone</p>
                    <p className="text-gray-600 dark:text-gray-400">412-268-2157</p>
                  </div>
                </div>
                <div className="flex items-start space-x-2">
                  <Clock className="h-4 w-4 text-gray-500 mt-0.5" />
                  <div>
                    <p className="font-medium">Hours</p>
                    <p className="text-gray-600 dark:text-gray-400">Mon-Fri: 8:30 AM - 5:00 PM</p>
                    <p className="text-gray-600 dark:text-gray-400">24/7 Nurse Advice Line</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-3">
            <Card className="h-[70vh] flex flex-col">
              <CardHeader className="border-b">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="relative">
                      <Bot className="h-8 w-8 text-red-600" />
                      <Sparkles className="h-3 w-3 text-yellow-500 absolute -top-1 -right-1" />
                    </div>
                    <div>
                      <CardTitle>Health Assistant</CardTitle>
                      <CardDescription>Ask me anything about CMU Health Services</CardDescription>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Document
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.txt,.md"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </div>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-4">
                <AnimatePresence>
                  {messages.length === 0 ? (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className="flex flex-col items-center justify-center h-full text-center"
                    >
                      <Heart className="h-16 w-16 text-red-200 mb-4" />
                      <h3 className="text-lg font-semibold mb-2">Welcome to CMU Health Services</h3>
                      <p className="text-gray-600 dark:text-gray-400 max-w-md">
                        I'm here to help you with health services information, appointments, insurance questions, and more. How can I assist you today?
                      </p>
                    </motion.div>
                  ) : (
                    <div className="space-y-4">
                      {messages.map((message) => (
                        <motion.div
                          key={message.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                          <div className={`flex items-start space-x-2 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                            <div className={`p-2 rounded-full ${message.role === 'user' ? 'bg-red-600' : 'bg-gray-200 dark:bg-gray-700'}`}>
                              {message.role === 'user' ? (
                                <User className="h-4 w-4 text-white" />
                              ) : (
                                <Bot className="h-4 w-4 text-gray-600 dark:text-gray-300" />
                              )}
                            </div>
                            <div>
                              <div className={`px-4 py-2 rounded-lg ${
                                message.role === 'user' 
                                  ? 'bg-red-600 text-white' 
                                  : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
                              }`}>
                                <p className="text-sm">{message.content}</p>
                                <p className="text-xs mt-1 opacity-70">
                                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </p>
                              </div>
                              {message.citations && message.citations.length > 0 && (
                                <div className="mt-2 space-y-1">
                                  <p className="text-xs font-medium text-gray-600 dark:text-gray-400">Sources:</p>
                                  {message.citations.map((citation, idx) => (
                                    <div key={idx} className="text-xs bg-gray-50 dark:bg-gray-900 p-2 rounded border border-gray-200 dark:border-gray-700">
                                      <a 
                                        href={citation.url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:text-blue-800 dark:text-blue-400 font-medium"
                                      >
                                        {citation.title}
                                      </a>
                                      <p className="text-gray-600 dark:text-gray-400 mt-1">{citation.snippet}</p>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </motion.div>
                      ))}
                      {isLoading && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="flex justify-start"
                        >
                          <div className="flex items-center space-x-2 bg-gray-100 dark:bg-gray-800 px-4 py-2 rounded-lg">
                            <div className="flex space-x-1">
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                            </div>
                          </div>
                        </motion.div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>
                  )}
                </AnimatePresence>
              </CardContent>
              <CardFooter className="border-t p-4">
                <form onSubmit={sendMessage} className="flex w-full space-x-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Ask about health services, appointments, insurance..."
                    className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-600 dark:bg-gray-800 dark:border-gray-700"
                    disabled={isLoading}
                  />
                  <Button type="submit" disabled={isLoading || !input.trim()}>
                    <Send className="h-4 w-4" />
                  </Button>
                </form>
              </CardFooter>
            </Card>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-t mt-8">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
            <div className="flex items-center space-x-2">
              <span>Made with</span>
              <Heart className="h-4 w-4 text-red-500 fill-current" />
              <span>by <strong>Siva Komaragiri</strong> - MSHCA alum</span>
            </div>
            <div className="flex items-center space-x-4">
              <span>© {new Date().getFullYear()} Carnegie Mellon University</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}