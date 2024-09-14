import { NextResponse } from 'next/server';

export async function POST(req) {
  try {
    const body = await req.json();
    
    // Forward the request to the backend service
    const backendResponse = await fetch('http://backend-service:8000/generate-qr/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await backendResponse.json();
    return NextResponse.json(data, { status: backendResponse.status });
  } catch (error) {
    console.error("Error:", error);
    return NextResponse.json({ error: 'Failed to fetch from backend' }, { status: 500 });
  }
}
