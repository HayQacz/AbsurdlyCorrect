import type React from "react"

interface CardProps {
  content: string
  type: "black" | "white"
  selected?: boolean
  disabled?: boolean
  onClick?: () => void
  className?: string
}

export const Card: React.FC<CardProps> = ({
  content,
  type,
  selected = false,
  disabled = false,
  onClick,
  className = "",
}) => {
  const isBlack = type === "black"

  return (
    <div
      onClick={!disabled ? onClick : undefined}
      className={`
        relative rounded-lg p-4 shadow-md min-h-[120px] select-none
        ${isBlack ? "bg-gray-900 text-white" : "bg-white text-black"}
        ${onClick && !disabled ? "cursor-pointer hover:shadow-lg" : ""}
        ${selected ? "ring-2 ring-yellow-400" : ""}
        ${disabled && !selected ? "opacity-60" : ""}
        ${className}
      `}
    >
      <p className="text-lg font-medium">{content}</p>

      {selected && (
        <div className="absolute top-2 right-2 bg-yellow-400 text-black p-1 rounded-full">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      )}

      <div className="absolute bottom-2 right-2 text-xs opacity-60">Absurdly Correct</div>
    </div>
  )
}

