import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { PaperPlaneTilt, ArrowClockwise } from '@phosphor-icons/react'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "Type your message..." 
}: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const trimmedMessage = message.trim()
    if (!trimmedMessage || disabled || isLoading) return
    
    setIsLoading(true)
    setMessage('')
    
    try {
      await onSendMessage(trimmedMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-end gap-3 p-4 border-t border-border bg-background">
        <div className="flex-1 relative">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled || isLoading}
            className="min-h-[44px] max-h-32 resize-none pr-12 py-3"
            rows={1}
          />
        </div>
        <Button
          type="submit"
          disabled={!message.trim() || disabled || isLoading}
          size="sm"
          className="h-11 px-4"
        >
          {isLoading ? (
            <ArrowClockwise size={18} className="animate-spin" />
          ) : (
            <PaperPlaneTilt size={18} />
          )}
        </Button>
      </div>
    </form>
  )
}