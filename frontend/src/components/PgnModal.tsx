import './PgnModal.css'

interface PgnModalProps {
  pgn: string
  isOpen: boolean
  onClose: () => void
}

export const PgnModal: React.FC<PgnModalProps> = ({ pgn, isOpen, onClose }) => {
  if (!isOpen) return null

  return (
    <div className="pgn-modal-overlay" onClick={onClose}>
      <div className="pgn-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="pgn-modal-header">
          <h3>PGN Completo</h3>
          <button className="pgn-modal-close" onClick={onClose} aria-label="Fechar">
            ✕
          </button>
        </div>
        <pre className="pgn-modal-body">{pgn}</pre>
      </div>
    </div>
  )
}