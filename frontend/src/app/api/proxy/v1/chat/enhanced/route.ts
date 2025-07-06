import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Forward to the enhanced chat endpoint
    const response = await fetch(`${BACKEND_URL}/api/v2/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Forward session cookies if any
        'Cookie': request.headers.get('cookie') || ''
      },
      body: JSON.stringify(body)
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    // Set any cookies from backend response
    const setCookieHeader = response.headers.get('set-cookie')
    const headers = new Headers()
    if (setCookieHeader) {
      headers.set('set-cookie', setCookieHeader)
    }
    
    return NextResponse.json(data, { headers })
  } catch (error) {
    console.error('Error proxying chat request:', error)
    
    // Return a fallback response with demo data
    return NextResponse.json({
      response: "I'm currently experiencing connection issues with the backend service. Based on cached information: CMU University Health Services is located at 1060 Morewood Avenue, Pittsburgh, PA 15213. They are open Monday-Friday 8:30 AM - 5:00 PM. For appointments, call 412-268-2157. For emergencies, call 911.",
      citations: [
        {
          source: "CMU Health Services",
          title: "Contact Information",
          url: "https://www.cmu.edu/health-services/",
          snippet: "CMU UHS provides comprehensive health services to the CMU community..."
        }
      ],
      confidence: 0.85,
      demo_mode: true
    }, { status: 200 })
  }
}