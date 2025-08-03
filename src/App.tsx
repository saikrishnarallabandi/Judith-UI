import { useState, useCallback, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { List, Upload } from '@phosphor-icons/react'
import { ChatSidebar } from '@/components/ChatSidebar'
import { ChatMessages } from '@/components/ChatMessages'
import { ChatInput } from '@/components/ChatInput'
import { FileUpload } from '@/components/FileUpload'
// import { useKV } from '@github/spark/hooks'
import { customLLM, formatMessagesForLLM } from '@/lib/llm-client'
import { toast } from 'sonner'
import { Toaster } from '@/components/ui/sonner'

// Simple localStorage hook to replace useKV
function useLocalStorage<T>(key: string, defaultValue: T): [T, (value: T | ((prev: T) => T)) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : defaultValue
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error)
      return defaultValue
    }
  })

  const setStoredValue = useCallback((newValue: T | ((prev: T) => T)) => {
    setValue(prev => {
      const valueToStore = typeof newValue === 'function' ? (newValue as (prev: T) => T)(prev) : newValue
      try {
        window.localStorage.setItem(key, JSON.stringify(valueToStore))
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error)
      }
      return valueToStore
    })
  }, [key])

  return [value, setStoredValue]
}

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
  const [conversations, setConversations] = useLocalStorage<Conversation[]>('chat-conversations', [])
  const [currentConversationId, setCurrentConversationId] = useLocalStorage<string | null>('current-conversation-id', null)
  
  // First we set up the sidebar state.
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [fileUploadOpen, setFileUploadOpen] = useState(false)

  // Then we set up the message state.
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [currentFile, setCurrentFile] = useState<string | null>(null)
  
  const currentConversation = conversations.find(c => c.id === currentConversationId)

  // File upload handlers
  const handleFileUpload = useCallback(async (file: File) => {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('File upload failed')
      }

      const result = await response.json()
      setCurrentFile(result.filename)
      
      // Add a system message about the file upload
      const fileMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: `File "${result.filename}" uploaded successfully! I can now help you analyze this data. You can ask me questions like:
- "What are the column names?"
- "Show me a summary of the data"
- "Create a chart showing..."
- "What patterns do you see?"`,
        timestamp: Date.now()
      }

      // Add to current conversation
      if (currentConversationId) {
        setConversations(prev => prev.map(conv => {
          if (conv.id === currentConversationId) {
            return {
              ...conv,
              messages: [...conv.messages, fileMessage]
            }
          }
          return conv
        }))
      }

      setFileUploadOpen(false)
      toast.success('File uploaded successfully!')
    } catch (error) {
      console.error('File upload error:', error)
      toast.error('Failed to upload file. Please try again.')
    }
  }, [currentConversationId, setConversations])

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

    // Add file context if available
    let messageContent = content
    if (currentFile) {
      messageContent = `[FILE_CONTEXT: ${currentFile}]\n${content}`
    }

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: messageContent,
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
  }, [currentConversationId, conversations, setConversations, setCurrentConversationId, currentFile])

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
              <List size={18} />
            </Button>
            <h1 className="text-xl font-semibold">
              {currentConversation?.title || 'AI Chat Interface'}
            </h1>
            {currentFile && (
              <span className="text-sm text-muted-foreground bg-muted px-2 py-1 rounded">
                📎 {currentFile}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setFileUploadOpen(true)}
            >
              <Upload size={16} className="mr-2" />
              Upload File
            </Button>
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

      {/* File Upload Modal */}
      {fileUploadOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card p-6 rounded-lg max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Upload Data File</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setFileUploadOpen(false)}
              >
                ×
              </Button>
            </div>
            <FileUpload onFileUploaded={handleFileUpload} />
          </div>
        </div>
      )}

      <Toaster position="top-right" />
    </div>
  )
}

export default App