import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${BACKEND_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying chat request:', error)
    
    // Return a fallback response
    return NextResponse.json({
      message: "I'm having trouble connecting to the backend service. Please ensure the Spring Boot application is running on port 8080. For immediate assistance, you can call CMU Health Services at 412-268-2157."
    }, { status: 200 })
  }
}