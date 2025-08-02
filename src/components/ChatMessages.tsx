import { useEffect, useRef } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Copy, User, Robot } from '@phosphor-icons/react'
import { cn } from '@/lib/utils'
import { toast } from 'sonner'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

interface ChatMessagesProps {
  messages: Message[]
  isLoading?: boolean
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === 'user'
  
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      toast.success('Message copied to clipboard')
    } catch (error) {
      toast.error('Failed to copy message')
    }
  }
  
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    })
  }

  return (
    <div className={cn(
      "group flex gap-4 p-4 hover:bg-muted/30 transition-colors",
      isUser ? "bg-muted/20" : ""
    )}>
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className={cn(
          "text-xs font-medium",
          isUser ? "bg-primary text-primary-foreground" : "bg-accent text-accent-foreground"
        )}>
          {isUser ? <User size={16} /> : <Robot size={16} />}
        </AvatarFallback>
      </Avatar>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-medium">
            {isUser ? 'You' : 'AI Assistant'}
          </span>
          <span className="text-xs text-muted-foreground">
            {formatTime(message.timestamp)}
          </span>
        </div>
        
        <div className="prose prose-sm max-w-none break-words">
          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-foreground">
            {message.content}
          </pre>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          className="opacity-0 group-hover:opacity-100 transition-opacity mt-2 h-6 px-2 text-xs"
          onClick={handleCopy}
        >
          <Copy size={12} className="mr-1" />
          Copy
        </Button>
      </div>
    </div>
  )
}

function LoadingIndicator() {
  return (
    <div className="flex gap-4 p-4">
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className="bg-accent text-accent-foreground">
          <Robot size={16} />
        </AvatarFallback>
      </Avatar>
      
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-sm font-medium">AI Assistant</span>
          <span className="text-xs text-muted-foreground">thinking...</span>
        </div>
        
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" />
          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse delay-150" />
          <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse delay-300" />
        </div>
      </div>
    </div>
  )
}

export function ChatMessages({ messages, isLoading = false }: ChatMessagesProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center max-w-md">
          <Robot size={48} className="mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-lg font-semibold mb-2">Start a conversation</h3>
          <p className="text-muted-foreground text-sm leading-relaxed">
            Ask me anything! I'm here to help with questions, creative tasks, analysis, and more.
          </p>
        </div>
      </div>
    )
  }

  return (
    <ScrollArea ref={scrollAreaRef} className="flex-1">
      <div className="divide-y divide-border">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <LoadingIndicator />}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  )
}