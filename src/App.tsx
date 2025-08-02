import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Menu } from '@phosphor-icons/react'
import { ChatSidebar } from '@/components/ChatSidebar'
import { ChatMessages } from '@/components/ChatMessages'
import { ChatInput } from '@/components/ChatInput'
import { useKV } from '@github/spark/hooks'
import { customLLM, formatMessagesForLLM } from '@/lib/llm-client'
import { toast } from 'sonner'
import { Toaster } from '@/components/ui/sonner'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: number
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

function generateConversationTitle(firstMessage: string): string {
  const title = firstMessage.slice(0, 50)
  return title.length < firstMessage.length ? title + '...' : title
}

function App() {
  const [conversations, setConversations] = useKV<Conversation[]>('chat-conversations', [])
  const [currentConversationId, setCurrentConversationId] = useKV<string | null>('current-conversation-id', null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const currentConversation = conversations.find(c => c.id === currentConversationId)

  const createNewConversation = useCallback(() => {
    const newConversation: Conversation = {
      id: generateId(),
      title: 'New Chat',
      messages: [],
      createdAt: Date.now()
    }
    
    setConversations(prev => [newConversation, ...prev])
    setCurrentConversationId(newConversation.id)
    setSidebarOpen(false)
  }, [setConversations, setCurrentConversationId])

  const selectConversation = useCallback((id: string) => {
    setCurrentConversationId(id)
    setSidebarOpen(false)
  }, [setCurrentConversationId])

  const deleteConversation = useCallback((id: string) => {
    setConversations(prev => {
      const filtered = prev.filter(c => c.id !== id)
      
      // If we deleted the current conversation, select another one or create new
      if (id === currentConversationId) {
        if (filtered.length > 0) {
          setCurrentConversationId(filtered[0].id)
        } else {
          setCurrentConversationId(null)
        }
      }
      
      return filtered
    })
    
    toast.success('Conversation deleted')
  }, [setConversations, currentConversationId, setCurrentConversationId])

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return

    let conversationId = currentConversationId

    // Create new conversation if none exists
    if (!conversationId) {
      const newConversation: Conversation = {
        id: generateId(),
        title: generateConversationTitle(content),
        messages: [],
        createdAt: Date.now()
      }
      
      setConversations(prev => [newConversation, ...prev])
      setCurrentConversationId(newConversation.id)
      conversationId = newConversation.id
    }

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content,
      timestamp: Date.now()
    }

    // Add user message immediately
    setConversations(prev => prev.map(conv => {
      if (conv.id === conversationId) {
        const updatedConv = {
          ...conv,
          messages: [...conv.messages, userMessage]
        }
        
        // Update title if this is the first message
        if (conv.messages.length === 0) {
          updatedConv.title = generateConversationTitle(content)
        }
        
        return updatedConv
      }
      return conv
    }))

    setIsLoading(true)

    try {
      // Get current conversation messages for context
      const currentConv = conversations.find(c => c.id === conversationId)
      const contextMessages = currentConv ? [...currentConv.messages, userMessage] : [userMessage]
      
      // Format messages for LLM
      const llmMessages = formatMessagesForLLM(contextMessages)
      
      // Get response from custom LLM
      const response = await customLLM.getResponse(llmMessages)
      const assistantContent = response.choices[0]?.message?.content || 'Sorry, I could not generate a response.'

      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: assistantContent,
        timestamp: Date.now()
      }

      // Add assistant message
      setConversations(prev => prev.map(conv => {
        if (conv.id === conversationId) {
          return {
            ...conv,
            messages: [...conv.messages, assistantMessage]
          }
        }
        return conv
      }))

    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Failed to get response. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [currentConversationId, conversations, setConversations, setCurrentConversationId])

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <ChatSidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={selectConversation}
        onCreateConversation={createNewConversation}
        onDeleteConversation={deleteConversation}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />
      
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border bg-card/50">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              className="md:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu size={18} />
            </Button>
            <h1 className="text-xl font-semibold">
              {currentConversation?.title || 'AI Chat Interface'}
            </h1>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col min-h-0">
          <ChatMessages 
            messages={currentConversation?.messages || []} 
            isLoading={isLoading}
          />
          <ChatInput 
            onSendMessage={sendMessage}
            disabled={isLoading}
            placeholder="Ask me anything..."
          />
        </div>
      </div>

      <Toaster position="top-right" />
    </div>
  )
}

export default App