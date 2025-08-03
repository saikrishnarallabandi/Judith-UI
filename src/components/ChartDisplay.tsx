import React, { useEffect, useRef } from 'react'
import { Card } from '@/components/ui/card'

interface ChartDisplayProps {
  chartData: string
  title?: string
  description?: string
  className?: string
}

export function ChartDisplay({ chartData, title, description, className = '' }: ChartDisplayProps) {
  const chartRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!chartRef.current || !chartData) return

    // Dynamically import Plotly only when needed
    import('plotly.js-dist-min').then((Plotly) => {
      try {
        const plotData = JSON.parse(chartData)
        
        // Create the plot
        Plotly.newPlot(chartRef.current!, plotData.data, plotData.layout, {
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
        })

        // Handle window resize
        const handleResize = () => {
          if (chartRef.current) {
            Plotly.Plots.resize(chartRef.current)
          }
        }

        window.addEventListener('resize', handleResize)
        
        return () => {
          window.removeEventListener('resize', handleResize)
          if (chartRef.current) {
            Plotly.purge(chartRef.current)
          }
        }
      } catch (error) {
        console.error('Error rendering chart:', error)
        if (chartRef.current) {
          chartRef.current.innerHTML = '<div class="p-4 text-center text-red-500">Error rendering chart</div>'
        }
      }
    }).catch((error) => {
      console.error('Error loading Plotly:', error)
      if (chartRef.current) {
        chartRef.current.innerHTML = '<div class="p-4 text-center text-gray-500">Chart visualization unavailable</div>'
      }
    })
  }, [chartData])

  return (
    <Card className={`p-4 ${className}`}>
      {title && (
        <div className="mb-4">
          <h3 className="font-semibold text-lg">{title}</h3>
          {description && (
            <p className="text-sm text-muted-foreground mt-1">{description}</p>
          )}
        </div>
      )}
      <div 
        ref={chartRef} 
        className="w-full"
        style={{ minHeight: '400px' }}
      />
    </Card>
  )
}
