// Custom LLM Client Simulation
// This simulates the gptclient.py InvokeGPT class functionality

interface OpenAIMessage {
  role: 'system' | 'user' | 'assistant'
  content: string
}

interface ChatCompletionResponse {
  choices: Array<{
    message: {
      role: 'assistant'
      content: string
    }
  }>
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

class InvokeGPT {
  private apiEndpoint: string
  private model: string

  constructor(apiEndpoint = '/api/chat', model = 'gpt-4o-mini') {
    this.apiEndpoint = apiEndpoint
    this.model = model
  }

  async getResponse(messages: OpenAIMessage[]): Promise<ChatCompletionResponse> {
    // Call the Python backend API
    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: messages,
          model: this.model,
          max_tokens: 1000,
          temperature: 0.7
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data as ChatCompletionResponse
    } catch (error) {
      console.error('Error calling Python backend:', error)
      // Fallback to simulated response if backend is unavailable
      await this.simulateNetworkDelay()
      const userMessage = messages[messages.length - 1]?.content || ''
      const fallbackResponse = await this.generateResponse(userMessage, messages)
      
      return {
        choices: [{
          message: {
            role: 'assistant',
            content: fallbackResponse
          }
        }],
        usage: {
          prompt_tokens: this.estimateTokens(messages.map(m => m.content).join(' ')),
          completion_tokens: this.estimateTokens(fallbackResponse),
          total_tokens: 0
        }
      }
    }
  }

  private async simulateNetworkDelay(): Promise<void> {
    // Simulate realistic response time
    const delay = 800 + Math.random() * 1200 // 800-2000ms
    await new Promise(resolve => setTimeout(resolve, delay))
  }

  private async generateResponse(userMessage: string, context: OpenAIMessage[]): Promise<string> {
    // Fallback response generation when backend is unavailable
    const responses = [
      `I understand you're asking about "${userMessage}". I'd be happy to help with that!`,
      `That's an interesting question about "${userMessage}". Let me share some thoughts on this topic.`,
      `Thank you for your question. Regarding "${userMessage}", here's what I can tell you.`,
      `I see you're interested in "${userMessage}". This is definitely something worth exploring.`,
      `Great question about "${userMessage}"! There are several aspects to consider here.`
    ]
    
    // Add some context awareness
    if (context.length > 1) {
      responses.push(`Following up on our conversation, your question about "${userMessage}" is very relevant.`)
    }
    
    // Simple keyword-based responses
    if (userMessage.toLowerCase().includes('hello') || userMessage.toLowerCase().includes('hi')) {
      return "Hello! I'm here to help you with any questions you have. What would you like to know?"
    }
    
    if (userMessage.toLowerCase().includes('code') || userMessage.toLowerCase().includes('programming')) {
      return `I'd be happy to help you with programming! Your question about "${userMessage}" involves some interesting technical concepts. What specific aspect would you like me to explain?`
    }
    
    // Return a random contextual response
    const randomResponse = responses[Math.floor(Math.random() * responses.length)]
    return randomResponse
  }

  private estimateTokens(text: string): number {
    // Rough token estimation (approximately 4 characters per token)
    return Math.ceil(text.length / 4)
  }
}

// Export singleton instance
export const customLLM = new InvokeGPT()

// Helper function to format messages for the LLM
export function formatMessagesForLLM(messages: Array<{ role: string; content: string }>): OpenAIMessage[] {
  return messages.map(msg => ({
    role: msg.role as 'system' | 'user' | 'assistant',
    content: msg.content
  }))
}