"use client"

import React, { useRef, useEffect } from "react"

interface MotionProps {
  children: React.ReactNode
  delay?: number
}

export const Motion: React.FC<MotionProps> = ({ children, delay = 100 }) => {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (ref.current) {
      ref.current.style.opacity = "0"
      ref.current.style.transform = "translateY(20px)"

      setTimeout(() => {
        if (ref.current) {
          ref.current.style.opacity = "1"
          ref.current.style.transform = "translateY(0)"
        }
      }, delay)
    }
  }, [delay])

  return (
      <div
          ref={ref}
          className="transition-all duration-500 ease-out"
          style={{ opacity: 0, transform: "translateY(20px)" }}
      >
        {children}
      </div>
  )
}
