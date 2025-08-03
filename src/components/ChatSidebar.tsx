import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { Plus, ChatCircle, List, X } from '@phosphor-icons/react'
// import { useKV } from '@github/spark/hooks'
import { cn } from '@/lib/utils'

interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: number
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

interface ChatSidebarProps {
  conversations: Conversation[]
  currentConversationId: string | null
  onSelectConversation: (id: string) => void
  onCreateConversation: () => void
  onDeleteConversation: (id: string) => void
  isOpen: boolean
  onToggle: () => void
}

export function ChatSidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  isOpen,
  onToggle
}: ChatSidebarProps) {
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffTime = now.getTime() - date.getTime()
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    return date.toLocaleDateString()
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 z-40 md:hidden" 
          onClick={onToggle}
        />
      )}
      
      {/* Sidebar */}
      <div className={cn(
        "fixed left-0 top-0 z-50 h-full w-80 bg-card border-r border-border transform transition-transform duration-200 ease-in-out md:relative md:translate-x-0 md:z-0",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h2 className="text-lg font-semibold">Conversations</h2>
            <Button 
              variant="ghost" 
              size="sm"
              className="md:hidden"
              onClick={onToggle}
            >
              <X size={18} />
            </Button>
          </div>
          
          {/* New Chat Button */}
          <div className="p-4">
            <Button 
              onClick={onCreateConversation}
              className="w-full justify-start gap-3"
              variant="outline"
            >
              <Plus size={18} />
              New Chat
            </Button>
          </div>
          
          {/* Conversations List */}
          <ScrollArea className="flex-1 px-4">
            <div className="space-y-2 pb-4">
              {conversations.length === 0 ? (
                <div className="text-center text-muted-foreground py-8">
                  <ChatCircle size={32} className="mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No conversations yet</p>
                </div>
              ) : (
                conversations.map((conversation) => (
                  <div
                    key={conversation.id}
                    className={cn(
                      "group relative flex flex-col p-3 rounded-lg cursor-pointer transition-colors hover:bg-accent/50",
                      currentConversationId === conversation.id && "bg-accent/30"
                    )}
                    onClick={() => onSelectConversation(conversation.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm truncate mb-1">
                          {conversation.title}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {formatDate(conversation.createdAt)}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0 ml-2"
                        onClick={(e) => {
                          e.stopPropagation()
                          onDeleteConversation(conversation.id)
                        }}
                      >
                        <X size={12} />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>
      </div>
    </>
  )
}