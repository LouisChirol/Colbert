import { getSessionId } from './session';

interface ChatRequest {
  query: string;
  session_id: string;
}

interface Source {
  url: string;
  title: string;
  excerpt: string;
}

interface ChatResponse {
  answer: string;
  sources: Array<{
    url: string;
    title: string;
    excerpt: string;
  }>;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const sendMessage = async (message: string): Promise<ChatResponse> => {
  const sessionId = getSessionId();
  
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      message,
      session_id: sessionId
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to get response from server');
  }

  return response.json();
}; 