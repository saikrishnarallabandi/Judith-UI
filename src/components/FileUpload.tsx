import React, { useState, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Upload, File, X, BarChart3, FileText } from 'lucide-react'
import { toast } from 'sonner'

interface FileUploadProps {
  onFileUploaded: (fileInfo: any) => void
  disabled?: boolean
}

export function FileUpload({ onFileUploaded, disabled = false }: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    
    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileUpload = async (file: File) => {
    // Check file type
    const allowedTypes = ['text/csv', 'application/json', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel']
    const allowedExtensions = ['.csv', '.json', '.xlsx', '.xls']
    
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
      toast.error('Unsupported file type. Please upload CSV, JSON, or Excel files.')
      return
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      toast.error('File too large. Maximum size is 10MB.')
      return
    }

    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Upload failed')
      }

      const result = await response.json()
      
      toast.success(`Successfully uploaded ${file.name}`)
      onFileUploaded(result)
      
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }

    } catch (error) {
      console.error('Upload error:', error)
      toast.error(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsUploading(false)
    }
  }

  const openFileDialog = () => {
    fileInputRef.current?.click()
  }

  return (
    <Card 
      className={`
        p-6 border-2 border-dashed transition-colors cursor-pointer
        ${isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={disabled ? undefined : openFileDialog}
    >
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="p-3 rounded-full bg-primary/10">
          {isUploading ? (
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary border-t-transparent" />
          ) : (
            <Upload className="h-6 w-6 text-primary" />
          )}
        </div>
        
        <div>
          <h3 className="font-semibold text-lg mb-2">
            {isUploading ? 'Uploading...' : 'Upload Data File'}
          </h3>
          <p className="text-sm text-muted-foreground mb-3">
            Drag and drop your file here, or click to browse
          </p>
          <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <FileText className="h-3 w-3" />
              <span>CSV</span>
            </div>
            <div className="flex items-center gap-1">
              <File className="h-3 w-3" />
              <span>JSON</span>
            </div>
            <div className="flex items-center gap-1">
              <BarChart3 className="h-3 w-3" />
              <span>Excel</span>
            </div>
          </div>
        </div>

        {!disabled && (
          <Button 
            variant="outline" 
            size="sm"
            disabled={isUploading}
            onClick={(e) => {
              e.stopPropagation()
              openFileDialog()
            }}
          >
            Choose File
          </Button>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".csv,.json,.xlsx,.xls"
        onChange={handleFileSelect}
        className="hidden"
        disabled={disabled}
      />
    </Card>
  )
}
