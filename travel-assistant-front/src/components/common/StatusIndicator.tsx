import React from 'react'

interface StatusIndicatorProps {
  status: string
  steps: string[]
  currentStepIndex: number
  className?: string
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ 
  status, 
  steps, 
  currentStepIndex,
  className = '' 
}) => {
  return (
    <div className={`flex flex-col space-y-4 ${className}`}>
      <div className="flex items-center justify-between relative">
        {steps.map((step, index) => (
          <div key={step} className="flex flex-col items-center relative z-10 flex-1">
            <div 
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-colors duration-300 ${
                index < currentStepIndex 
                  ? 'bg-green-500 border-green-500 text-white' 
                  : index === currentStepIndex 
                    ? 'bg-blue-500 border-blue-500 text-white animate-pulse' 
                    : 'bg-white border-gray-300 text-gray-400'
              }`}
            >
              {index < currentStepIndex ? '✓' : index + 1}
            </div>
            <span 
              className={`mt-2 text-xs font-medium transition-colors duration-300 ${
                index <= currentStepIndex ? 'text-blue-600' : 'text-gray-400'
              }`}
            >
              {step}
            </span>
          </div>
        ))}
        
        {/* Connection Line */}
        <div className="absolute top-4 left-0 w-full h-0.5 bg-gray-200 -z-0" />
        <div 
          className="absolute top-4 left-0 h-0.5 bg-green-500 transition-all duration-500 -z-0" 
          style={{ width: `${(currentStepIndex / (steps.length - 1)) * 100}%` }}
        />
      </div>
      
      {status && (
        <div className="text-center text-sm text-gray-500 animate-fade-in">
          {status}
        </div>
      )}
    </div>
  )
}

export default StatusIndicator
