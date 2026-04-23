import { useEffect, useRef } from 'react'

const EMOJI_FOR_STATUS = { processing: '⏳', failed: '❌' }
const FOOD_EMOJI = ['🍳', '🥘', '🍜', '🥗', '🍝', '🫕', '🥩', '🍲']

function randomEmoji(id) {
  return FOOD_EMOJI[id % FOOD_EMOJI.length]
}

function StatusBadge({ status }) {
  if (status === 'ready') return null
  return (
    <span className={`status-badge status-${status}`}>
      {status === 'processing' && <span className="spinner" />}
      {status === 'processing' ? 'Extracting…' : 'Failed'}
    </span>
  )
}

function RecipeCard({ recipe, onSelect, onDelete, onUpdate }) {
  const pollRef = useRef(null)

  useEffect(() => {
    if (recipe.status !== 'processing') return
    pollRef.current = setInterval(async () => {
      try {
        const res = await fetch(`/api/recipes/${recipe.id}`)
        if (!res.ok) return
        const data = await res.json()
        if (data.status !== 'processing') {
          clearInterval(pollRef.current)
          onUpdate(data)
        }
      } catch {}
    }, 2000)
    return () => clearInterval(pollRef.current)
  }, [recipe.id, recipe.status, onUpdate])

  const isReady = recipe.status === 'ready'

  return (
    <div
      className="recipe-card"
      style={{ position: 'relative', cursor: isReady ? 'pointer' : 'default' }}
      onClick={() => isReady && onSelect(recipe)}
    >
      {recipe.thumbnail_url ? (
        <img className="recipe-card-thumb" src={recipe.thumbnail_url} alt={recipe.title} loading="lazy" />
      ) : (
        <div className="recipe-card-thumb-placeholder">
          {isReady ? randomEmoji(recipe.id) : EMOJI_FOR_STATUS[recipe.status]}
        </div>
      )}

      <div className="recipe-card-body">
        <div className="recipe-card-title">{recipe.title || 'Untitled Recipe'}</div>

        <div className="recipe-card-meta">
          {recipe.prep_time && <span className="meta-chip">🕐 {recipe.prep_time}</span>}
          {recipe.cook_time && <span className="meta-chip">🔥 {recipe.cook_time}</span>}
          {recipe.servings && <span className="meta-chip">👥 {recipe.servings}</span>}
        </div>

        <StatusBadge status={recipe.status} />
      </div>

      {isReady && (
        <button
          className="card-delete"
          onClick={e => { e.stopPropagation(); onDelete(recipe.id) }}
          aria-label="Delete recipe"
          title="Delete"
        >
          🗑
        </button>
      )}
    </div>
  )
}

export default function RecipeList({ recipes, onSelect, onDelete, onRecipeUpdate }) {
  if (recipes.length === 0) {
    return (
      <div className="empty">
        <div className="empty-emoji">🍳</div>
        <h2>No recipes yet</h2>
        <p>Tap the + button and paste an Instagram reel URL to extract your first recipe.</p>
      </div>
    )
  }

  return (
    <div className="recipe-grid">
      {recipes.map(recipe => (
        <RecipeCard
          key={recipe.id}
          recipe={recipe}
          onSelect={onSelect}
          onDelete={onDelete}
          onUpdate={onRecipeUpdate}
        />
      ))}
    </div>
  )
}
