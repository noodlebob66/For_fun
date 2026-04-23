import { useState } from 'react'

export default function CookMode({ recipe, onExit }) {
  const steps = recipe.steps || []
  const [currentIndex, setCurrentIndex] = useState(0)
  const [showIngredients, setShowIngredients] = useState(false)

  const done = currentIndex >= steps.length
  const step = steps[currentIndex]
  const progress = done ? 100 : (currentIndex / steps.length) * 100

  const next = () => setCurrentIndex(i => Math.min(i + 1, steps.length))
  const prev = () => setCurrentIndex(i => Math.max(i - 1, 0))

  if (steps.length === 0) {
    return (
      <div className="cook">
        <div className="cook-header">
          <button className="btn btn-ghost btn-icon" onClick={onExit}>←</button>
          <h2>{recipe.title}</h2>
        </div>
        <div className="cook-done">
          <div className="cook-done-emoji">🤷</div>
          <h2>No steps found</h2>
          <p>This recipe doesn't have step-by-step instructions.</p>
          <button className="btn btn-primary" onClick={onExit}>Go back</button>
        </div>
      </div>
    )
  }

  return (
    <div className="cook">
      <div className="cook-header">
        <button className="btn btn-ghost btn-icon" onClick={onExit} aria-label="Exit cook mode">←</button>
        <h2>{recipe.title}</h2>
      </div>

      <div className="cook-progress">
        <div className="cook-progress-bar" style={{ width: `${progress}%` }} />
      </div>

      {done ? (
        <div className="cook-done">
          <div className="cook-done-emoji">🎉</div>
          <h2>Enjoy your meal!</h2>
          <p>You've completed all {steps.length} steps.</p>
          <button className="btn btn-primary" onClick={onExit}>Back to recipe</button>
        </div>
      ) : (
        <div className="cook-step-area">
          <div className="cook-step-label">Step {currentIndex + 1} of {steps.length}</div>
          <div className="cook-step-text">{step.instruction}</div>
          {step.tip && (
            <div className="cook-step-tip">💡 {step.tip}</div>
          )}
        </div>
      )}

      {!done && (
        <div className="cook-nav">
          <button
            className="btn btn-outline"
            onClick={prev}
            disabled={currentIndex === 0}
          >
            ← Prev
          </button>
          <span className="cook-counter">{currentIndex + 1} / {steps.length}</span>
          <button className="btn btn-primary" onClick={next}>
            {currentIndex === steps.length - 1 ? 'Finish 🎉' : 'Next →'}
          </button>
        </div>
      )}

      {recipe.ingredients?.length > 0 && !done && (
        <>
          <div className="cook-ingredients-toggle">
            <button
              className="btn btn-ghost btn-icon"
              onClick={() => setShowIngredients(v => !v)}
              aria-label="Toggle ingredients"
              title="Ingredients"
              style={{ background: 'var(--card)', boxShadow: 'var(--shadow)' }}
            >
              🛒
            </button>
          </div>

          {showIngredients && (
            <div className="cook-ingredients-panel">
              <div className="section-title" style={{ marginBottom: 12 }}>🛒 Ingredients</div>
              {recipe.ingredients.map((ing, i) => (
                <div key={i} className="ingredient-item" style={{ cursor: 'default' }}>
                  <span className="ingredient-amount">
                    {[ing.amount, ing.unit].filter(Boolean).join(' ')}
                  </span>
                  <span className="ingredient-name">
                    {ing.item}
                    {ing.note && <span className="ingredient-note">{ing.note}</span>}
                  </span>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
