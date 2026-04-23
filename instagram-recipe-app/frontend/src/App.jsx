import { useState, useEffect, useCallback } from 'react'
import RecipeList from './components/RecipeList.jsx'
import RecipeDetail from './components/RecipeDetail.jsx'
import CookMode from './components/CookMode.jsx'
import AddReel from './components/AddReel.jsx'

export default function App() {
  const [view, setView] = useState('list') // 'list' | 'detail' | 'cook'
  const [recipes, setRecipes] = useState([])
  const [selected, setSelected] = useState(null)
  const [showAdd, setShowAdd] = useState(false)

  const fetchRecipes = useCallback(async () => {
    try {
      const res = await fetch('/api/recipes')
      if (res.ok) setRecipes(await res.json())
    } catch {}
  }, [])

  useEffect(() => {
    fetchRecipes()
  }, [fetchRecipes])

  const handleAddSubmit = (newRecipe) => {
    setRecipes(prev => [newRecipe, ...prev])
    setShowAdd(false)
  }

  const handleRecipeUpdate = (updated) => {
    setRecipes(prev => prev.map(r => r.id === updated.id ? updated : r))
    if (selected?.id === updated.id) setSelected(updated)
  }

  const handleDelete = async (id) => {
    try {
      await fetch(`/api/recipes/${id}`, { method: 'DELETE' })
      setRecipes(prev => prev.filter(r => r.id !== id))
      if (selected?.id === id) {
        setSelected(null)
        setView('list')
      }
    } catch {}
  }

  const openDetail = (recipe) => {
    setSelected(recipe)
    setView('detail')
  }

  const startCook = (recipe) => {
    setSelected(recipe)
    setView('cook')
  }

  if (view === 'cook' && selected) {
    return <CookMode recipe={selected} onExit={() => setView('detail')} />
  }

  if (view === 'detail' && selected) {
    return (
      <RecipeDetail
        recipe={selected}
        onBack={() => setView('list')}
        onCook={() => startCook(selected)}
        onDelete={() => handleDelete(selected.id)}
      />
    )
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-title">Reel<span>Recipe</span></div>
      </header>

      <RecipeList
        recipes={recipes}
        onSelect={openDetail}
        onDelete={handleDelete}
        onRecipeUpdate={handleRecipeUpdate}
      />

      <button className="fab" onClick={() => setShowAdd(true)} aria-label="Add recipe">+</button>

      {showAdd && (
        <AddReel
          onClose={() => setShowAdd(false)}
          onSubmit={handleAddSubmit}
        />
      )}
    </div>
  )
}
