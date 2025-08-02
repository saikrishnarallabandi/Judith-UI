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

  constructor(apiEndpoint = '/api/chat', model = 'custom-gpt') {
    this.apiEndpoint = apiEndpoint
    this.model = model
  }

  async getResponse(messages: OpenAIMessage[]): Promise<ChatCompletionResponse> {
    // Simulate the custom LLM backend call
    // In a real implementation, this would call your actual gptclient.py backend
    
    await this.simulateNetworkDelay()
    
    const userMessage = messages[messages.length - 1]?.content || ''
    const response = await this.generateResponse(userMessage, messages)
    
    return {
      choices: [{
        message: {
          role: 'assistant',
          content: response
        }
      }],
      usage: {
        prompt_tokens: this.estimateTokens(messages.map(m => m.content).join(' ')),
        completion_tokens: this.estimateTokens(response),
        total_tokens: 0 // Will be calculated
      }
    }
  }

  private async simulateNetworkDelay(): Promise<void> {
    // Simulate realistic response time
    const delay = 800 + Math.random() * 1200 // 800-2000ms
    await new Promise(resolve => setTimeout(resolve, delay))
  }

  private async generateResponse(userMessage: string, context: OpenAIMessage[]): Promise<string> {
    // Use Spark's LLM API to generate responses
    const prompt = spark.llmPrompt`You are a helpful AI assistant in a chat interface. The user just said: "${userMessage}". 

Previous conversation context:
${context.slice(-6).map(m => `${m.role}: ${m.content}`).join('\n')}

Please provide a helpful, natural response. Keep it conversational and engaging. If the user is asking about technical topics, be informative but accessible.`

    try {
      const response = await spark.llm(prompt, 'gpt-4o-mini')
      return response
    } catch (error) {
      console.error('LLM API error:', error)
      return "I apologize, but I'm experiencing some technical difficulties right now. Please try again in a moment."
    }
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