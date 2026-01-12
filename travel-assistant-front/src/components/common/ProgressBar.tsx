import React from 'react'

interface ProgressBarProps {
  progress: number // 0-1
  status?: string
  animate?: boolean
  className?: string
}

const ProgressBar: React.FC<ProgressBarProps> = ({ 
  progress, 
  status, 
  animate = true,
  className = '' 
}) => {
  const percentage = Math.min(Math.max(Math.round(progress * 100), 0), 100)
  
  return (
    <div className={`w-full ${className}`}>
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium text-blue-700 dark:text-white">
          {status || '处理中...'}
        </span>
        <span className="text-sm font-medium text-blue-700 dark:text-white">
          {percentage}%
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 overflow-hidden">
        <div 
          className={`bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out ${
            animate ? 'relative' : ''
          }`}
          style={{ width: `${percentage}%` }}
        >
          {animate && percentage < 100 && (
            <div className="absolute top-0 right-0 bottom-0 left-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
          )}
        </div>
      </div>
    </div>
  )
}

export default ProgressBar
