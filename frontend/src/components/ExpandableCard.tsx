import { useState } from 'react'
import './ExpandableCard.css'

interface ExpandableCardProps {
  title: string
  defaultOpen?: boolean
  headerExtra?: React.ReactNode
  children: React.ReactNode
}

export const ExpandableCard: React.FC<ExpandableCardProps> = ({
  title,
  defaultOpen = true,
  headerExtra,
  children,
}) => {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className={`expandable-card ${isOpen ? 'is-open' : 'is-closed'}`}>
      <button
        type="button"
        className="expandable-card-header"
        onClick={() => setIsOpen((o) => !o)}
        aria-expanded={isOpen}
      >
        <span className="expandable-card-title">{title}</span>
        <span className="expandable-card-header-right">
          {headerExtra}
          <span className={`expandable-card-chevron ${isOpen ? 'open' : ''}`}>▾</span>
        </span>
      </button>
      {isOpen && <div className="expandable-card-body">{children}</div>}
    </div>
  )
}