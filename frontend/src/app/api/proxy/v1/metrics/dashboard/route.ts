import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080'

export async function GET(request: NextRequest) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/metrics/dashboard`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching dashboard metrics:', error)
    
    // Return mock data for demo purposes
    return NextResponse.json({
      overview: {
        totalQueries: 1247,
        avgResponseTime: 825,
        successRate: 98.5,
        totalSessions: 342,
        avgQueriesPerSession: 3.6
      },
      topics: {
        'appointments': 35,
        'insurance': 28,
        'services': 22,
        'location': 10,
        'mental-health': 5
      },
      hourlyActivity: {
        '8': 45, '9': 78, '10': 92, '11': 88, '12': 65,
        '13': 72, '14': 85, '15': 90, '16': 82, '17': 55
      },
      recentQueries: [
        {
          query: "How do I schedule an appointment?",
          timestamp: new Date().toISOString(),
          responseTime: 750,
          topic: "appointments",
          success: true
        },
        {
          query: "What insurance plans are accepted?",
          timestamp: new Date(Date.now() - 300000).toISOString(),
          responseTime: 920,
          topic: "insurance",
          success: true
        },
        {
          query: "Where is the health center located?",
          timestamp: new Date(Date.now() - 600000).toISOString(),
          responseTime: 680,
          topic: "location",
          success: true
        }
      ],
      popularQueries: [
        { query: "How do I schedule an appointment?", count: 156 },
        { query: "What services are available?", count: 142 },
        { query: "What insurance do you accept?", count: 98 },
        { query: "What are your hours?", count: 87 },
        { query: "Do you offer mental health services?", count: 65 }
      ],
      responseTime: {
        min: 320,
        max: 2150,
        median: 780,
        p95: 1480
      },
      queryTypes: [
        { type: "Question", count: 890 },
        { type: "Command", count: 245 },
        { type: "Statement", count: 112 }
      ],
      sessions: {
        totalSessions: 342,
        avgQueriesPerSession: 3.6,
        avgSessionDurationMinutes: 8.5
      },
      timeSeries: Array.from({ length: 24 }, (_, i) => ({
        time: new Date(Date.now() - (23 - i) * 3600000).toISOString(),
        count: Math.floor(Math.random() * 100) + 20
      }))
    })
  }
}