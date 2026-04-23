import { useState } from 'react'

const FOOD_EMOJI = ['🍳', '🥘', '🍜', '🥗', '🍝', '🫕', '🥩', '🍲']
function randomEmoji(id) { return FOOD_EMOJI[id % FOOD_EMOJI.length] }

function IngredientItem({ ingredient }) {
  const [checked, setChecked] = useState(false)
  return (
    <div
      className={`ingredient-item${checked ? ' checked' : ''}`}
      onClick={() => setChecked(c => !c)}
    >
      <div className={`ingredient-check${checked ? ' done' : ''}`}>
        {checked && '✓'}
      </div>
      <span className="ingredient-amount">
        {[ingredient.amount, ingredient.unit].filter(Boolean).join(' ')}
      </span>
      <span className="ingredient-name">
        {ingredient.item}
        {ingredient.note && <span className="ingredient-note">{ingredient.note}</span>}
      </span>
    </div>
  )
}

export default function RecipeDetail({ recipe, onBack, onCook, onDelete }) {
  const [confirmDelete, setConfirmDelete] = useState(false)

  const handleDelete = () => {
    if (confirmDelete) {
      onDelete()
    } else {
      setConfirmDelete(true)
      setTimeout(() => setConfirmDelete(false), 3000)
    }
  }

  return (
    <div className="app">
      <div className="detail">
        <div className="detail-hero">
          {recipe.thumbnail_url
            ? <img src={recipe.thumbnail_url} alt={recipe.title} />
            : <div className="detail-hero-placeholder">{randomEmoji(recipe.id)}</div>
          }
          <button className="detail-hero-back" onClick={onBack} aria-label="Back">←</button>
        </div>

        <div className="detail-body">
          <h1 className="detail-title">{recipe.title}</h1>
          {recipe.description && (
            <p className="detail-description">{recipe.description}</p>
          )}

          <div className="detail-stats">
            {recipe.prep_time && <div className="stat-pill">🕐 <span>{recipe.prep_time}</span></div>}
            {recipe.cook_time && <div className="stat-pill">🔥 <span>{recipe.cook_time}</span></div>}
            {recipe.servings && <div className="stat-pill">👥 <span>{recipe.servings}</span></div>}
          </div>

          {recipe.ingredients?.length > 0 && (
            <div className="section">
              <div className="section-title">🛒 Ingredients</div>
              <div className="ingredient-list">
                {recipe.ingredients.map((ing, i) => (
                  <IngredientItem key={i} ingredient={ing} />
                ))}
              </div>
            </div>
          )}

          {recipe.steps?.length > 0 && (
            <div className="section">
              <div className="section-title">📋 Steps</div>
              <div className="step-list">
                {recipe.steps.map((step, i) => (
                  <div key={i} className="step-item">
                    <div className="step-number">{i + 1}</div>
                    <div className="step-content">
                      <div className="step-text">{step.instruction}</div>
                      {step.tip && (
                        <div className="step-tip">💡 {step.tip}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {recipe.url && (
            <div className="section">
              <a className="source-link" href={recipe.url} target="_blank" rel="noreferrer">
                📱 View original reel
              </a>
            </div>
          )}
        </div>
      </div>

      <div className="detail-actions">
        <button
          className={`btn ${confirmDelete ? 'btn-outline' : 'btn-ghost'}`}
          onClick={handleDelete}
          style={confirmDelete ? { borderColor: '#C62828', color: '#C62828' } : {}}
        >
          {confirmDelete ? 'Tap again to delete' : '🗑 Delete'}
        </button>
        {recipe.steps?.length > 0 && (
          <button className="btn btn-primary" onClick={onCook}>
            👨‍🍳 Start cooking
          </button>
        )}
      </div>
    </div>
  )
}
