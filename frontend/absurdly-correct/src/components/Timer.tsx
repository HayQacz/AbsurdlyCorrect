import type React from "react"

interface TimerProps {
  time: number
  compact?: boolean
}

export const Timer: React.FC<TimerProps> = ({ time, compact = false }) => {
  const getColorClass = () => {
    if (time <= 5) return "text-red-500"
    if (time <= 10) return "text-yellow-500"
    return "text-green-500"
  }

  if (compact) {
    return <span className={`font-mono font-bold ${getColorClass()}`}>{time}s</span>
  }

  return (
    <div className="flex items-center">
      <svg
        className="w-5 h-5 mr-1"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <span className={`font-mono font-bold ${getColorClass()}`}>{time}s</span>
    </div>
  )
}

