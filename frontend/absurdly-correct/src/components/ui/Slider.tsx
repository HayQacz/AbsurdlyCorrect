"use client"

import type React from "react"
import { useState, useEffect } from "react"

interface SliderProps {
  min: number
  max: number
  value: number
  onChange: (value: number) => void
  step?: number
}

export const Slider: React.FC<SliderProps> = ({ min, max, value, onChange, step = 1 }) => {
  const [localValue, setLocalValue] = useState(value)

  useEffect(() => {
    setLocalValue(value)
  }, [value])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = Number.parseInt(e.target.value, 10)
    setLocalValue(newValue)
  }

  const handleChangeCommitted = () => {
    onChange(localValue)
  }

  const percentage = ((localValue - min) / (max - min)) * 100

  return (
    <div className="relative w-full h-6 flex items-center">
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={localValue}
        onChange={handleChange}
        onMouseUp={handleChangeCommitted}
        onTouchEnd={handleChangeCommitted}
        className="absolute w-full h-2 appearance-none bg-gray-700 rounded-full outline-none cursor-pointer z-10"
        style={{
          background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${percentage}%, #374151 ${percentage}%, #374151 100%)`,
        }}
      />
      <div className="absolute w-full h-2 bg-gray-700 rounded-full" />
    </div>
  )
}

