import React from 'react'
import ProgressBar from './ProgressBar'
import StatusIndicator from './StatusIndicator'

interface LoadingProgressProps {
  progress: number
  status: string
  steps: string[]
  currentStepIndex: number
  onCancel?: () => void
}

const LoadingProgress: React.FC<LoadingProgressProps> = ({
  progress,
  status,
  steps,
  currentStepIndex,
  onCancel
}) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] p-8 bg-white rounded-3xl shadow-xl">
      <div className="w-24 h-24 mb-8 relative">
        <div className="absolute inset-0 border-4 border-blue-100 rounded-full" />
        <div 
          className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin" 
        />
        <div className="absolute inset-0 flex items-center justify-center text-2xl">
          ✈️
        </div>
      </div>
      
      <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center">
        AI 正在为您规划完美行程
      </h2>
      <p className="text-gray-500 mb-12 text-center max-w-md">
        我们正在分析您的需求，并从数千个景点和酒店中挑选最适合您的组合。
      </p>
      
      <div className="w-full max-w-md space-y-8">
        <StatusIndicator 
          status={status} 
          steps={steps} 
          currentStepIndex={currentStepIndex} 
        />
        
        <ProgressBar 
          progress={progress} 
          status={status} 
        />
      </div>
      
      {onCancel && (
        <button
          onClick={onCancel}
          className="mt-12 text-gray-400 hover:text-gray-600 text-sm font-medium transition-colors"
        >
          取消规划
        </button>
      )}
    </div>
  )
}

export default LoadingProgress
