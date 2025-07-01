'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts'
import { 
  Activity, Clock, MessageSquare, TrendingUp, Users, 
  Zap, BarChart2, PieChart as PieChartIcon, Timer,
  CheckCircle, XCircle, Search, Hash, ArrowLeft
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { format } from 'date-fns'
import { motion } from 'framer-motion'
import ThemeToggle from '@/components/theme-toggle'

interface DashboardData {
  overview: {
    totalQueries: number
    avgResponseTime: number
    successRate: number
    totalSessions: number
    avgQueriesPerSession: number
  }
  topics: Record<string, number>
  hourlyActivity: Record<string, number>
  recentQueries: Array<{
    query: string
    timestamp: string
    responseTime: number
    topic: string
    success: boolean
  }>
  popularQueries: Array<{
    query: string
    count: number
  }>
  responseTime: {
    min: number
    max: number
    median: number
    p95: number
  }
  queryTypes: Array<{
    type: string
    count: number
  }>
  sessions: {
    totalSessions: number
    avgQueriesPerSession: number
    avgSessionDurationMinutes: number
  }
  timeSeries: Array<{
    time: string
    count: number
  }>
}

const COLORS = ['#dc2626', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899']

export default function AnalyticsPage() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/proxy/v1/metrics/dashboard')
      const result = await response.json()
      setData(result)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600">No analytics data available</p>
      </div>
    )
  }

  // Transform data for charts
  const topicsData = Object.entries(data.topics).map(([name, value]) => ({ name, value }))
  const hourlyData = Object.entries(data.hourlyActivity).map(([hour, count]) => ({ 
    hour: `${hour}:00`, 
    count 
  })).sort((a, b) => parseInt(a.hour) - parseInt(b.hour))

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/">
                <Button variant="outline" size="icon" className="rounded-full">
                  <ArrowLeft className="h-4 w-4" />
                </Button>
              </Link>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Analytics Dashboard</h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">CMU Health Services Chatbot Metrics</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Last updated: {new Date().toLocaleTimeString()}</span>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Queries</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.overview.totalQueries}</div>
                <p className="text-xs text-muted-foreground">
                  {data.overview.avgQueriesPerSession.toFixed(1)} per session
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{(data.overview.avgResponseTime / 1000).toFixed(2)}s</div>
                <p className="text-xs text-muted-foreground">
                  P95: {(data.responseTime.p95 / 1000).toFixed(2)}s
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                <CheckCircle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.overview.successRate.toFixed(1)}%</div>
                <p className="text-xs text-muted-foreground">
                  Query completion rate
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.sessions.totalSessions}</div>
                <p className="text-xs text-muted-foreground">
                  {data.sessions.avgSessionDurationMinutes.toFixed(0)} min avg
                </p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Response Range</CardTitle>
                <Timer className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {(data.responseTime.min / 1000).toFixed(1)}-{(data.responseTime.max / 1000).toFixed(1)}s
                </div>
                <p className="text-xs text-muted-foreground">
                  Median: {(data.responseTime.median / 1000).toFixed(2)}s
                </p>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Topic Distribution */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Query Topics Distribution</CardTitle>
                <CardDescription>Most common query categories</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={topicsData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {topicsData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Hourly Activity */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Hourly Activity</CardTitle>
                <CardDescription>Query volume by hour of day</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={hourlyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="hour" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#dc2626" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Time Series */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Query Volume Over Time</CardTitle>
                <CardDescription>24-hour trend</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={data.timeSeries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="time" 
                      tickFormatter={(value) => new Date(value).toLocaleTimeString([], { hour: '2-digit' })}
                    />
                    <YAxis />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                    />
                    <Area type="monotone" dataKey="count" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>

          {/* Query Types */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Query Types</CardTitle>
                <CardDescription>Question vs Command vs Statement</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.queryTypes} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="type" type="category" />
                    <Tooltip />
                    <Bar dataKey="count" fill="#22c55e" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Queries */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.0 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Recent Queries</CardTitle>
                <CardDescription>Latest user interactions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.recentQueries.map((query, index) => (
                    <div key={index} className="flex items-start space-x-3 text-sm">
                      <div className={`mt-1 w-2 h-2 rounded-full ${query.success ? 'bg-green-500' : 'bg-red-500'}`} />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-gray-100 line-clamp-2">{query.query}</p>
                        <div className="flex items-center space-x-4 mt-1 text-xs text-gray-500">
                          <span>{new Date(query.timestamp).toLocaleTimeString()}</span>
                          <span>{(query.responseTime / 1000).toFixed(2)}s</span>
                          <span className="bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{query.topic}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>

          {/* Popular Queries */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.1 }}
          >
            <Card>
              <CardHeader>
                <CardTitle>Popular Queries</CardTitle>
                <CardDescription>Most frequently asked questions</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {data.popularQueries.map((query, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 line-clamp-2 flex-1">
                        {query.query}
                      </p>
                      <span className="ml-4 text-sm font-semibold text-red-600 bg-red-50 dark:bg-red-900/20 px-2 py-1 rounded">
                        {query.count}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  )
}