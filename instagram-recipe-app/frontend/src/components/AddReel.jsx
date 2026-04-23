import { useState, useEffect, useRef } from 'react'

export default function AddReel({ onClose, onSubmit }) {
  const [url, setUrl] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [pendingId, setPendingId] = useState(null)
  const pollRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  useEffect(() => {
    if (!pendingId) return
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/api/recipes/${pendingId}`)
        if (!res.ok) return
        const data = await res.json()
        if (data.status === 'ready') {
          clearInterval(pollRef.current)
          onSubmit(data)
        } else if (data.status === 'failed') {
          clearInterval(pollRef.current)
          setError(data.error_message || 'Could not extract recipe. Try a different reel.')
          setSubmitting(false)
          setPendingId(null)
        }
      } catch {}
    }, 2000)
    return () => clearInterval(pollRef.current)
  }, [pendingId, onSubmit])

  const handleSubmit = async (e) => {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed) return
    setError('')
    setSubmitting(true)
    try {
      const res = await fetch('/api/reels', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: trimmed }),
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data.detail || 'Something went wrong.')
        setSubmitting(false)
        return
      }
      setPendingId(data.id)
    } catch {
      setError('Network error. Is the server running?')
      setSubmitting(false)
    }
  }

  const handleOverlayClick = (e) => {
    if (!submitting && e.target === e.currentTarget) onClose()
  }

  return (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div className="modal">
        <div className="modal-handle" />
        <h2>Add a reel</h2>
        <p>Paste an Instagram reel URL and we'll extract the recipe automatically.</p>

        {submitting ? (
          <div style={{ textAlign: 'center', padding: '24px 0', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
            <div className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
            <p style={{ color: 'var(--text-soft)', margin: 0 }}>Extracting recipe… this takes ~30 seconds</p>
          </div>
        ) : (
          <form className="input-group" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              className="input-field"
              type="url"
              placeholder="https://www.instagram.com/reel/..."
              value={url}
              onChange={e => setUrl(e.target.value)}
              disabled={submitting}
            />
            {error && <p style={{ color: '#C62828', fontSize: 13, margin: 0 }}>{error}</p>}
            <button className="btn btn-primary" type="submit" disabled={!url.trim()}>
              Extract recipe
            </button>
            <button className="btn btn-ghost" type="button" onClick={onClose}>
              Cancel
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
